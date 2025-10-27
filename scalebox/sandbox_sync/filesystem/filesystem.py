from io import IOBase
from typing import IO, Iterator, List, Literal, Optional, Union, overload

import httpcore
import httpx
import urllib3
from packaging.version import Version

from ... import csx_connect
from ...connection_config import (
    KEEPALIVE_PING_HEADER,
    KEEPALIVE_PING_INTERVAL_SEC,
    ConnectionConfig,
    Username,
)
from ...exceptions import InvalidArgumentException, TemplateException
from ...generated import api_pb2, api_pb2_connect
from ...generated.api import (
    ENVD_API_DOWNLOAD_FILES_ROUTE,
    ENVD_API_UPLOAD_FILES_ROUTE,
    handle_envd_api_exception,
)
from ...generated.rpc import authentication_header, handle_rpc_exception
from ...generated.versions import ENVD_VERSION_RECURSIVE_WATCH
from ...sandbox.filesystem.filesystem import (
    EntryInfo,
    FileType,
    WriteEntry,
    WriteInfo,
    map_file_type,
)
from ...sandbox_sync.filesystem.watch_handle import WatchHandle


class Filesystem:
    """
    Module for interacting with the filesystem in the sandbox.
    """

    def __init__(
        self,
        envd_api_url: str,
        envd_version: Optional[str],
        connection_config: ConnectionConfig,
        pool: urllib3.PoolManager,
        envd_api: httpx.Client,
    ) -> None:
        self._envd_api_url = envd_api_url
        self._envd_version = envd_version
        self._connection_config = connection_config
        self._pool = pool
        self._envd_api = envd_api

        self._rpc = api_pb2_connect.FilesystemClient(
            envd_api_url,
            http_client=pool
        )
        self._headers = self._connection_config.headers

    @overload
    def read(
        self,
        path: str,
        format: Literal["text"] = "text",
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> str:
        """
        Read file content as a `str`.

        :param path: Path to the file
        :param user: Run the operation as this user
        :param format: Format of the file content—`text` by default
        :param request_timeout: Timeout for the request in **seconds**

        :return: File content as a `str`
        """
        ...

    @overload
    def read(
        self,
        path: str,
        format: Literal["bytes"],
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> bytearray:
        """
        Read file content as a `bytearray`.

        :param path: Path to the file
        :param user: Run the operation as this user
        :param format: Format of the file content—`bytes`
        :param request_timeout: Timeout for the request in **seconds**

        :return: File content as a `bytearray`
        """
        ...

    @overload
    def read(
        self,
        path: str,
        format: Literal["stream"],
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> Iterator[bytes]:
        """
        Read file content as a `Iterator[bytes]`.

        :param path: Path to the file
        :param user: Run the operation as this user
        :param format: Format of the file content—`stream`
        :param request_timeout: Timeout for the request in **seconds**

        :return: File content as an `Iterator[bytes]`
        """
        ...

    def read(
        self,
        path: str,
        format: Literal["text", "bytes", "stream"] = "text",
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ):
        # Use the /download/ endpoint from sandboxagent.go
        download_url = f"/download/{path.lstrip('/')}"
        
        r = self._envd_api.get(
            download_url,
            timeout=self._connection_config.get_request_timeout(request_timeout),
        )

        err = handle_envd_api_exception(r)
        if err:
            raise err

        if format == "text":
            return r.text
        elif format == "bytes":
            return bytearray(r.content)
        elif format == "stream":
            return r.iter_bytes()

    @overload
    def write(
        self,
        path: str,
        data: Union[str, bytes, IO],
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> WriteInfo:
        """
        Write content to a file on the path.

        Writing to a file that doesn't exist creates the file.

        Writing to a file that already exists overwrites the file.

        Writing to a file at path that doesn't exist creates the necessary directories.

        :param path: Path to the file
        :param data: Data to write to the file, can be a `str`, `bytes`, or `IO`.
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request in **seconds**

        :return: Information about the written file
        """

    @overload
    def write(
        self,
        files: List[WriteEntry],
        user: Optional[Username] = "user",
        request_timeout: Optional[float] = None,
    ) -> List[WriteInfo]:
        """
        Writes a list of files to the filesystem.
        When writing to a file that doesn't exist, the file will get created.
        When writing to a file that already exists, the file will get overwritten.
        When writing to a file that's in a directory that doesn't exist, you'll get an error.

        :param files: list of files to write
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request
        :return: Information about the written files
        """

    def write(
        self,
        path_or_files: Union[str, List[WriteEntry]],
        data_or_user: Union[str, bytes, IO, Username] = "user",
        user_or_request_timeout: Optional[Union[float, Username]] = None,
        request_timeout_or_none: Optional[float] = None,
    ) -> Union[WriteInfo, List[WriteInfo]]:
        path, write_files, user, request_timeout = None, [], "user", None
        if isinstance(path_or_files, str):
            if isinstance(data_or_user, list):
                raise Exception(
                    "Cannot specify both path and array of files. You have to specify either path and data for a single file or an array for multiple files."
                )
            path, write_files, user, request_timeout = (
                path_or_files,
                [{"path": path_or_files, "data": data_or_user}],
                user_or_request_timeout or "user",
                request_timeout_or_none,
            )
        else:
            if path_or_files is None:
                raise Exception("Path or files are required")
            path, write_files, user, request_timeout = (
                None,
                path_or_files,
                data_or_user,
                user_or_request_timeout,
            )

        # Allow passing empty list of files
        if len(write_files) == 0:
            return []

        # Use the /upload endpoint from sandboxagent.go
        # This endpoint expects multipart/form-data with 'file' field and 'path' form field
        results = []
        for file in write_files:
            file_path, file_data = file["path"], file["data"]
            
            # Prepare file data
            if isinstance(file_data, str):
                file_content = file_data.encode('utf-8')
            elif isinstance(file_data, bytes):
                file_content = file_data
            elif isinstance(file_data, IOBase):
                file_content = file_data.read()
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')
            else:
                raise ValueError(f"Unsupported data type for file {file_path}")

            # Prepare multipart form data
            files = [("file", (file_path, file_content))]
            data = {"path": file_path}

            r = self._envd_api.post(
                "/upload",
                files=files,
                data=data,
                timeout=self._connection_config.get_request_timeout(request_timeout),
            )

            err = handle_envd_api_exception(r)
            if err:
                raise err
            
            # For now, create a mock WriteInfo since sandboxagent.go returns plain text
            # In a real implementation, you might want to enhance the server to return JSON
            results.append(WriteInfo(
                path=file_path,
                name=file_path.split('/')[-1] if '/' in file_path else file_path,
                type=FileType.FILE,
            ))

        # Return appropriate response based on input format
        if len(results) == 1 and path:
            return results[0]
        else:
            return results

    def list(
        self,
        path: str,
        depth: Optional[int] = 1,
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> List[EntryInfo]:
        """
        List entries in a directory.

        :param path: Path to the directory
        :param depth: Depth of the directory to list
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request in **seconds**

        :return: List of entries in the directory
        """
        if depth is not None and depth < 1:
            raise InvalidArgumentException("depth should be at least 1")

        try:
            res = self._rpc.list_dir(
                api_pb2.ListDirRequest(path=path, depth=depth),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )

            entries: List[EntryInfo] = []
            for entry in res.entries:
                event_type = map_file_type(entry.type)

                if event_type:
                    entries.append(
                        EntryInfo(
                            name=entry.name,
                            type=event_type,
                            path=entry.path,
                            size=entry.size,
                            mode=entry.mode,
                            permissions=entry.permissions,
                            owner=entry.owner,
                            group=entry.group,
                            modified_time=entry.modified_time.ToDatetime(),
                            # Optional, we can't directly access symlink_target otherwise if will be "" instead of None
                            symlink_target=(
                                entry.symlink_target
                                if entry.HasField("symlink_target")
                                else None
                            ),
                        )
                    )

            return entries
        except Exception as e:
            raise handle_rpc_exception(e)

    def exists(
        self,
        path: str,
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> bool:
        """
        Check if a file or a directory exists.

        :param path: Path to a file or a directory
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request in **seconds**

        :return: `True` if the file or directory exists, `False` otherwise
        """
        try:
            self._rpc.stat(
                api_pb2.StatRequest(path=path),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )
            return True

        except Exception as e:
            if "no such file or directory" in str(e):
                return False
            raise handle_rpc_exception(e)

    def get_info(
        self,
        path: str,
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> EntryInfo:
        """
        Get information about a file or directory.

        :param path: Path to a file or a directory
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request in **seconds**

        :return: Information about the file or directory like name, type, and path
        """
        try:
            r = self._rpc.stat(
                api_pb2.StatRequest(path=path),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )

            return EntryInfo(
                name=r.entry.name,
                type=map_file_type(r.entry.type),
                path=r.entry.path,
                size=r.entry.size,
                mode=r.entry.mode,
                permissions=r.entry.permissions,
                owner=r.entry.owner,
                group=r.entry.group,
                modified_time=r.entry.modified_time.ToDatetime(),
                # Optional, we can't directly access symlink_target otherwise if will be "" instead of None
                symlink_target=(
                    r.entry.symlink_target
                    if r.entry.HasField("symlink_target")
                    else None
                ),
            )
        except Exception as e:
            raise handle_rpc_exception(e)

    def remove(
        self,
        path: str,
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> None:
        """
        Remove a file or a directory.

        :param path: Path to a file or a directory
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request in **seconds**
        """
        try:
            self._rpc.remove(
                api_pb2.RemoveRequest(path=path),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )
        except Exception as e:
            raise handle_rpc_exception(e)

    def rename(
        self,
        old_path: str,
        new_path: str,
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> EntryInfo:
        """
        Rename a file or directory.

        :param old_path: Path to the file or directory to rename
        :param new_path: New path to the file or directory
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request in **seconds**

        :return: Information about the renamed file or directory
        """
        try:
            r = self._rpc.move(
                api_pb2.MoveRequest(
                    source=old_path,
                    destination=new_path,
                ),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )

            return EntryInfo(
                name=r.entry.name,
                type=map_file_type(r.entry.type),
                path=r.entry.path,
                size=r.entry.size,
                mode=r.entry.mode,
                permissions=r.entry.permissions,
                owner=r.entry.owner,
                group=r.entry.group,
                modified_time=r.entry.modified_time.ToDatetime(),
                # Optional, we can't directly access symlink_target otherwise if will be "" instead of None
                symlink_target=(
                    r.entry.symlink_target
                    if r.entry.HasField("symlink_target")
                    else None
                ),
            )
        except Exception as e:
            raise handle_rpc_exception(e)

    def make_dir(
        self,
        path: str,
        user: Username = "user",
        request_timeout: Optional[float] = None,
    ) -> bool:
        """
        Create a new directory and all directories along the way if needed on the specified path.

        :param path: Path to a new directory. For example '/dirA/dirB' when creating 'dirB'.
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request in **seconds**

        :return: `True` if the directory was created, `False` if the directory already exists
        """
        try:
            self._rpc.make_dir(
                api_pb2.MakeDirRequest(path=path),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )

            return True
        except Exception as e:
            if "directory already exists" in str(e):
                return False
            raise handle_rpc_exception(e)

    def watch_dir(
        self,
        path: str,
        user: Username = "user",
        request_timeout: Optional[float] = None,
        recursive: bool = False,
    ) -> WatchHandle:
        """
        Watch directory for filesystem events.

        :param path: Path to a directory to watch
        :param user: Run the operation as this user
        :param request_timeout: Timeout for the request in **seconds**
        :param recursive: Watch directory recursively

        :return: `WatchHandle` object for stopping watching directory
        """
        if (
            recursive
            and self._envd_version is not None
            and Version(self._envd_version) < ENVD_VERSION_RECURSIVE_WATCH
        ):
            raise TemplateException(
                "You need to update the template to use recursive watching. "
                "You can do this by running `scalebox template build` in the directory with the template."
            )

        try:
            r = self._rpc.create_watcher(
                api_pb2.CreateWatcherRequest(path=path, recursive=recursive),
                self._headers,
                timeout_seconds=self._connection_config.get_request_timeout(
                    request_timeout
                ),
            )
        except Exception as e:
            raise handle_rpc_exception(e)

        return WatchHandle(self._rpc, r.watcher_id)
