# Generated Connect client code

from __future__ import annotations
from collections.abc import AsyncIterator
from collections.abc import Iterator
from collections.abc import Iterable
import aiohttp
import urllib3
import typing
import sys

from connectrpc.client_async import AsyncConnectClient
from connectrpc.client_sync import ConnectClient
from connectrpc.client_protocol import ConnectProtocol
from connectrpc.client_connect import ConnectProtocolError
from connectrpc.headers import HeaderInput
from connectrpc.server import ClientRequest
from connectrpc.server import ClientStream
from connectrpc.server import ServerResponse
from connectrpc.server import ServerStream
from connectrpc.server_sync import ConnectWSGI
from connectrpc.streams import StreamInput
from connectrpc.streams import AsyncStreamOutput
from connectrpc.streams import StreamOutput
from connectrpc.unary import UnaryOutput
from connectrpc.unary import ClientStreamingOutput

if typing.TYPE_CHECKING:
    # wsgiref.types was added in Python 3.11.
    if sys.version_info >= (3, 11):
        from wsgiref.types import WSGIApplication
    else:
        from _typeshed.wsgi import WSGIApplication

from . import api_pb2

class FilesystemClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_stat(
        self, req: api_pb2.StatRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.StatResponse]:
        """Low-level method to call Stat, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/Stat"
        return self._connect_client.call_unary(url, req, api_pb2.StatResponse,extra_headers, timeout_seconds)


    def stat(
        self, req: api_pb2.StatRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.StatResponse:
        response = self.call_stat(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_make_dir(
        self, req: api_pb2.MakeDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.MakeDirResponse]:
        """Low-level method to call MakeDir, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/MakeDir"
        return self._connect_client.call_unary(url, req, api_pb2.MakeDirResponse,extra_headers, timeout_seconds)


    def make_dir(
        self, req: api_pb2.MakeDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.MakeDirResponse:
        response = self.call_make_dir(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_move(
        self, req: api_pb2.MoveRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.MoveResponse]:
        """Low-level method to call Move, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/Move"
        return self._connect_client.call_unary(url, req, api_pb2.MoveResponse,extra_headers, timeout_seconds)


    def move(
        self, req: api_pb2.MoveRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.MoveResponse:
        response = self.call_move(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_list_dir(
        self, req: api_pb2.ListDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.ListDirResponse]:
        """Low-level method to call ListDir, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/ListDir"
        return self._connect_client.call_unary(url, req, api_pb2.ListDirResponse,extra_headers, timeout_seconds)


    def list_dir(
        self, req: api_pb2.ListDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.ListDirResponse:
        response = self.call_list_dir(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_remove(
        self, req: api_pb2.RemoveRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.RemoveResponse]:
        """Low-level method to call Remove, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/Remove"
        return self._connect_client.call_unary(url, req, api_pb2.RemoveResponse,extra_headers, timeout_seconds)


    def remove(
        self, req: api_pb2.RemoveRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.RemoveResponse:
        response = self.call_remove(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def watch_dir(
        self, req: api_pb2.WatchDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> Iterator[api_pb2.WatchDirResponse]:
        return self._watch_dir_iterator(req, extra_headers, timeout_seconds)

    def _watch_dir_iterator(
        self, req: api_pb2.WatchDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> Iterator[api_pb2.WatchDirResponse]:
        stream_output = self.call_watch_dir(req, extra_headers)
        err = stream_output.error()
        if err is not None:
            raise err
        yield from stream_output
        err = stream_output.error()
        if err is not None:
            raise err

    def call_watch_dir(
        self, req: api_pb2.WatchDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> StreamOutput[api_pb2.WatchDirResponse]:
        """Low-level method to call WatchDir, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/WatchDir"
        return self._connect_client.call_server_streaming(
            url, req, api_pb2.WatchDirResponse, extra_headers, timeout_seconds
        )

    def call_create_watcher(
        self, req: api_pb2.CreateWatcherRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.CreateWatcherResponse]:
        """Low-level method to call CreateWatcher, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/CreateWatcher"
        return self._connect_client.call_unary(url, req, api_pb2.CreateWatcherResponse,extra_headers, timeout_seconds)


    def create_watcher(
        self, req: api_pb2.CreateWatcherRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.CreateWatcherResponse:
        response = self.call_create_watcher(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_get_watcher_events(
        self, req: api_pb2.GetWatcherEventsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.GetWatcherEventsResponse]:
        """Low-level method to call GetWatcherEvents, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/GetWatcherEvents"
        return self._connect_client.call_unary(url, req, api_pb2.GetWatcherEventsResponse,extra_headers, timeout_seconds)


    def get_watcher_events(
        self, req: api_pb2.GetWatcherEventsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.GetWatcherEventsResponse:
        response = self.call_get_watcher_events(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_remove_watcher(
        self, req: api_pb2.RemoveWatcherRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.RemoveWatcherResponse]:
        """Low-level method to call RemoveWatcher, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/RemoveWatcher"
        return self._connect_client.call_unary(url, req, api_pb2.RemoveWatcherResponse,extra_headers, timeout_seconds)


    def remove_watcher(
        self, req: api_pb2.RemoveWatcherRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.RemoveWatcherResponse:
        response = self.call_remove_watcher(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncFilesystemClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_stat(
        self, req: api_pb2.StatRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.StatResponse]:
        """Low-level method to call Stat, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/Stat"
        return await self._connect_client.call_unary(url, req, api_pb2.StatResponse,extra_headers, timeout_seconds)

    async def stat(
        self, req: api_pb2.StatRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.StatResponse:
        response = await self.call_stat(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_make_dir(
        self, req: api_pb2.MakeDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.MakeDirResponse]:
        """Low-level method to call MakeDir, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/MakeDir"
        return await self._connect_client.call_unary(url, req, api_pb2.MakeDirResponse,extra_headers, timeout_seconds)

    async def make_dir(
        self, req: api_pb2.MakeDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.MakeDirResponse:
        response = await self.call_make_dir(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_move(
        self, req: api_pb2.MoveRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.MoveResponse]:
        """Low-level method to call Move, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/Move"
        return await self._connect_client.call_unary(url, req, api_pb2.MoveResponse,extra_headers, timeout_seconds)

    async def move(
        self, req: api_pb2.MoveRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.MoveResponse:
        response = await self.call_move(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_list_dir(
        self, req: api_pb2.ListDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.ListDirResponse]:
        """Low-level method to call ListDir, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/ListDir"
        return await self._connect_client.call_unary(url, req, api_pb2.ListDirResponse,extra_headers, timeout_seconds)

    async def list_dir(
        self, req: api_pb2.ListDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.ListDirResponse:
        response = await self.call_list_dir(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_remove(
        self, req: api_pb2.RemoveRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.RemoveResponse]:
        """Low-level method to call Remove, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/Remove"
        return await self._connect_client.call_unary(url, req, api_pb2.RemoveResponse,extra_headers, timeout_seconds)

    async def remove(
        self, req: api_pb2.RemoveRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.RemoveResponse:
        response = await self.call_remove(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def watch_dir(
        self, req: api_pb2.WatchDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncIterator[api_pb2.WatchDirResponse]:
        return self._watch_dir_iterator(req, extra_headers, timeout_seconds)

    async def _watch_dir_iterator(
        self, req: api_pb2.WatchDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncIterator[api_pb2.WatchDirResponse]:
        stream_output = await self.call_watch_dir(req, extra_headers)
        err = stream_output.error()
        if err is not None:
            raise err
        async with stream_output as stream:
            async for response in stream:
                yield response
            err = stream.error()
            if err is not None:
                raise err

    async def call_watch_dir(
        self, req: api_pb2.WatchDirRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncStreamOutput[api_pb2.WatchDirResponse]:
        """Low-level method to call WatchDir, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/WatchDir"
        return await self._connect_client.call_server_streaming(
            url, req, api_pb2.WatchDirResponse, extra_headers, timeout_seconds
        )

    async def call_create_watcher(
        self, req: api_pb2.CreateWatcherRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.CreateWatcherResponse]:
        """Low-level method to call CreateWatcher, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/CreateWatcher"
        return await self._connect_client.call_unary(url, req, api_pb2.CreateWatcherResponse,extra_headers, timeout_seconds)

    async def create_watcher(
        self, req: api_pb2.CreateWatcherRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.CreateWatcherResponse:
        response = await self.call_create_watcher(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_get_watcher_events(
        self, req: api_pb2.GetWatcherEventsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.GetWatcherEventsResponse]:
        """Low-level method to call GetWatcherEvents, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/GetWatcherEvents"
        return await self._connect_client.call_unary(url, req, api_pb2.GetWatcherEventsResponse,extra_headers, timeout_seconds)

    async def get_watcher_events(
        self, req: api_pb2.GetWatcherEventsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.GetWatcherEventsResponse:
        response = await self.call_get_watcher_events(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_remove_watcher(
        self, req: api_pb2.RemoveWatcherRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.RemoveWatcherResponse]:
        """Low-level method to call RemoveWatcher, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Filesystem/RemoveWatcher"
        return await self._connect_client.call_unary(url, req, api_pb2.RemoveWatcherResponse,extra_headers, timeout_seconds)

    async def remove_watcher(
        self, req: api_pb2.RemoveWatcherRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.RemoveWatcherResponse:
        response = await self.call_remove_watcher(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class FilesystemProtocol(typing.Protocol):
    def stat(self, req: ClientRequest[api_pb2.StatRequest]) -> ServerResponse[api_pb2.StatResponse]:
        ...
    def make_dir(self, req: ClientRequest[api_pb2.MakeDirRequest]) -> ServerResponse[api_pb2.MakeDirResponse]:
        ...
    def move(self, req: ClientRequest[api_pb2.MoveRequest]) -> ServerResponse[api_pb2.MoveResponse]:
        ...
    def list_dir(self, req: ClientRequest[api_pb2.ListDirRequest]) -> ServerResponse[api_pb2.ListDirResponse]:
        ...
    def remove(self, req: ClientRequest[api_pb2.RemoveRequest]) -> ServerResponse[api_pb2.RemoveResponse]:
        ...
    def watch_dir(self, req: ClientRequest[api_pb2.WatchDirRequest]) -> ServerStream[api_pb2.WatchDirResponse]:
        ...
    def create_watcher(self, req: ClientRequest[api_pb2.CreateWatcherRequest]) -> ServerResponse[api_pb2.CreateWatcherResponse]:
        ...
    def get_watcher_events(self, req: ClientRequest[api_pb2.GetWatcherEventsRequest]) -> ServerResponse[api_pb2.GetWatcherEventsResponse]:
        ...
    def remove_watcher(self, req: ClientRequest[api_pb2.RemoveWatcherRequest]) -> ServerResponse[api_pb2.RemoveWatcherResponse]:
        ...

FILESYSTEM_PATH_PREFIX = "/sandboxagent.Filesystem"

def wsgi_filesystem(implementation: FilesystemProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/sandboxagent.Filesystem/Stat", implementation.stat, api_pb2.StatRequest)
    app.register_unary_rpc("/sandboxagent.Filesystem/MakeDir", implementation.make_dir, api_pb2.MakeDirRequest)
    app.register_unary_rpc("/sandboxagent.Filesystem/Move", implementation.move, api_pb2.MoveRequest)
    app.register_unary_rpc("/sandboxagent.Filesystem/ListDir", implementation.list_dir, api_pb2.ListDirRequest)
    app.register_unary_rpc("/sandboxagent.Filesystem/Remove", implementation.remove, api_pb2.RemoveRequest)
    app.register_server_streaming_rpc("/sandboxagent.Filesystem/WatchDir", implementation.watch_dir, api_pb2.WatchDirRequest)
    app.register_unary_rpc("/sandboxagent.Filesystem/CreateWatcher", implementation.create_watcher, api_pb2.CreateWatcherRequest)
    app.register_unary_rpc("/sandboxagent.Filesystem/GetWatcherEvents", implementation.get_watcher_events, api_pb2.GetWatcherEventsRequest)
    app.register_unary_rpc("/sandboxagent.Filesystem/RemoveWatcher", implementation.remove_watcher, api_pb2.RemoveWatcherRequest)
    return app

class ProcessClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_list(
        self, req: api_pb2.ListRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.ListResponse]:
        """Low-level method to call List, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/List"
        return self._connect_client.call_unary(url, req, api_pb2.ListResponse,extra_headers, timeout_seconds)


    def list(
        self, req: api_pb2.ListRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.ListResponse:
        response = self.call_list(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def connect(
        self, req: api_pb2.ConnectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> Iterator[api_pb2.ConnectResponse]:
        return self._connect_iterator(req, extra_headers, timeout_seconds)

    def _connect_iterator(
        self, req: api_pb2.ConnectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> Iterator[api_pb2.ConnectResponse]:
        stream_output = self.call_connect(req, extra_headers)
        err = stream_output.error()
        if err is not None:
            raise err
        yield from stream_output
        err = stream_output.error()
        if err is not None:
            raise err

    def call_connect(
        self, req: api_pb2.ConnectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> StreamOutput[api_pb2.ConnectResponse]:
        """Low-level method to call Connect, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/Connect"
        return self._connect_client.call_server_streaming(
            url, req, api_pb2.ConnectResponse, extra_headers, timeout_seconds
        )

    def start(
        self, req: api_pb2.StartRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> Iterator[api_pb2.StartResponse]:
        return self._start_iterator(req, extra_headers, timeout_seconds)

    def _start_iterator(
        self, req: api_pb2.StartRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> Iterator[api_pb2.StartResponse]:
        stream_output = self.call_start(req, extra_headers)
        err = stream_output.error()
        if err is not None:
            raise err
        yield from stream_output
        err = stream_output.error()
        if err is not None:
            raise err

    def call_start(
        self, req: api_pb2.StartRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> StreamOutput[api_pb2.StartResponse]:
        """Low-level method to call Start, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/Start"
        return self._connect_client.call_server_streaming(
            url, req, api_pb2.StartResponse, extra_headers, timeout_seconds
        )

    def call_update(
        self, req: api_pb2.UpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.UpdateResponse]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/Update"
        return self._connect_client.call_unary(url, req, api_pb2.UpdateResponse,extra_headers, timeout_seconds)


    def update(
        self, req: api_pb2.UpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.UpdateResponse:
        response = self.call_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_stream_input(
        self, reqs: Iterable[api_pb2.StreamInputRequest], extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> ClientStreamingOutput[api_pb2.StreamInputResponse]:
        """Low-level method to call StreamInput, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/StreamInput"
        return self._connect_client.call_client_streaming(
            url, reqs, api_pb2.StreamInputResponse, extra_headers, timeout_seconds
        )

    def stream_input(
        self, reqs: Iterable[api_pb2.StreamInputRequest], extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.StreamInputResponse:
        client_stream_output = self.call_stream_input(reqs, extra_headers)
        err = client_stream_output.error()
        if err is not None:
            raise err
        msg = client_stream_output.message()
        if msg is None:
            raise RuntimeError('ClientStreamOutput has empty error and message')
        return msg

    def call_send_input(
        self, req: api_pb2.SendInputRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.SendInputResponse]:
        """Low-level method to call SendInput, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/SendInput"
        return self._connect_client.call_unary(url, req, api_pb2.SendInputResponse,extra_headers, timeout_seconds)


    def send_input(
        self, req: api_pb2.SendInputRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.SendInputResponse:
        response = self.call_send_input(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_send_signal(
        self, req: api_pb2.SendSignalRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.SendSignalResponse]:
        """Low-level method to call SendSignal, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/SendSignal"
        return self._connect_client.call_unary(url, req, api_pb2.SendSignalResponse,extra_headers, timeout_seconds)


    def send_signal(
        self, req: api_pb2.SendSignalRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.SendSignalResponse:
        response = self.call_send_signal(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncProcessClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_list(
        self, req: api_pb2.ListRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.ListResponse]:
        """Low-level method to call List, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/List"
        return await self._connect_client.call_unary(url, req, api_pb2.ListResponse,extra_headers, timeout_seconds)

    async def list(
        self, req: api_pb2.ListRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.ListResponse:
        response = await self.call_list(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def connect(
        self, req: api_pb2.ConnectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncIterator[api_pb2.ConnectResponse]:
        return self._connect_iterator(req, extra_headers, timeout_seconds)

    async def _connect_iterator(
        self, req: api_pb2.ConnectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncIterator[api_pb2.ConnectResponse]:
        stream_output = await self.call_connect(req, extra_headers)
        err = stream_output.error()
        if err is not None:
            raise err
        async with stream_output as stream:
            async for response in stream:
                yield response
            err = stream.error()
            if err is not None:
                raise err

    async def call_connect(
        self, req: api_pb2.ConnectRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncStreamOutput[api_pb2.ConnectResponse]:
        """Low-level method to call Connect, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/Connect"
        return await self._connect_client.call_server_streaming(
            url, req, api_pb2.ConnectResponse, extra_headers, timeout_seconds
        )

    def start(
        self, req: api_pb2.StartRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncIterator[api_pb2.StartResponse]:
        return self._start_iterator(req, extra_headers, timeout_seconds)

    async def _start_iterator(
        self, req: api_pb2.StartRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncIterator[api_pb2.StartResponse]:
        stream_output = await self.call_start(req, extra_headers)
        err = stream_output.error()
        if err is not None:
            raise err
        async with stream_output as stream:
            async for response in stream:
                yield response
            err = stream.error()
            if err is not None:
                raise err

    async def call_start(
        self, req: api_pb2.StartRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncStreamOutput[api_pb2.StartResponse]:
        """Low-level method to call Start, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/Start"
        return await self._connect_client.call_server_streaming(
            url, req, api_pb2.StartResponse, extra_headers, timeout_seconds
        )

    async def call_update(
        self, req: api_pb2.UpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.UpdateResponse]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/Update"
        return await self._connect_client.call_unary(url, req, api_pb2.UpdateResponse,extra_headers, timeout_seconds)

    async def update(
        self, req: api_pb2.UpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.UpdateResponse:
        response = await self.call_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_stream_input(
        self, reqs: StreamInput[api_pb2.StreamInputRequest], extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> ClientStreamingOutput[api_pb2.StreamInputResponse]:
        """Low-level method to call StreamInput, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/StreamInput"
        return await self._connect_client.call_client_streaming(
            url, reqs, api_pb2.StreamInputResponse, extra_headers, timeout_seconds
        )

    async def stream_input(
        self, reqs: StreamInput[api_pb2.StreamInputRequest], extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.StreamInputResponse:
        client_stream_output = await self.call_stream_input(reqs, extra_headers)
        err = client_stream_output.error()
        if err is not None:
            raise err
        msg = client_stream_output.message()
        if msg is None:
            raise RuntimeError('ClientStreamOutput has empty error and message')
        return msg

    async def call_send_input(
        self, req: api_pb2.SendInputRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.SendInputResponse]:
        """Low-level method to call SendInput, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/SendInput"
        return await self._connect_client.call_unary(url, req, api_pb2.SendInputResponse,extra_headers, timeout_seconds)

    async def send_input(
        self, req: api_pb2.SendInputRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.SendInputResponse:
        response = await self.call_send_input(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_send_signal(
        self, req: api_pb2.SendSignalRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.SendSignalResponse]:
        """Low-level method to call SendSignal, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.Process/SendSignal"
        return await self._connect_client.call_unary(url, req, api_pb2.SendSignalResponse,extra_headers, timeout_seconds)

    async def send_signal(
        self, req: api_pb2.SendSignalRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.SendSignalResponse:
        response = await self.call_send_signal(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class ProcessProtocol(typing.Protocol):
    def list(self, req: ClientRequest[api_pb2.ListRequest]) -> ServerResponse[api_pb2.ListResponse]:
        ...
    def connect(self, req: ClientRequest[api_pb2.ConnectRequest]) -> ServerStream[api_pb2.ConnectResponse]:
        ...
    def start(self, req: ClientRequest[api_pb2.StartRequest]) -> ServerStream[api_pb2.StartResponse]:
        ...
    def update(self, req: ClientRequest[api_pb2.UpdateRequest]) -> ServerResponse[api_pb2.UpdateResponse]:
        ...
    def stream_input(self, req: ClientStream[api_pb2.StreamInputRequest]) -> ServerResponse[api_pb2.StreamInputResponse]:
        ...
    def send_input(self, req: ClientRequest[api_pb2.SendInputRequest]) -> ServerResponse[api_pb2.SendInputResponse]:
        ...
    def send_signal(self, req: ClientRequest[api_pb2.SendSignalRequest]) -> ServerResponse[api_pb2.SendSignalResponse]:
        ...

PROCESS_PATH_PREFIX = "/sandboxagent.Process"

def wsgi_process(implementation: ProcessProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/sandboxagent.Process/List", implementation.list, api_pb2.ListRequest)
    app.register_server_streaming_rpc("/sandboxagent.Process/Connect", implementation.connect, api_pb2.ConnectRequest)
    app.register_server_streaming_rpc("/sandboxagent.Process/Start", implementation.start, api_pb2.StartRequest)
    app.register_unary_rpc("/sandboxagent.Process/Update", implementation.update, api_pb2.UpdateRequest)
    app.register_client_streaming_rpc("/sandboxagent.Process/StreamInput", implementation.stream_input, api_pb2.StreamInputRequest)
    app.register_unary_rpc("/sandboxagent.Process/SendInput", implementation.send_input, api_pb2.SendInputRequest)
    app.register_unary_rpc("/sandboxagent.Process/SendSignal", implementation.send_signal, api_pb2.SendSignalRequest)
    return app

class ExecutionServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def execute(
        self, req: api_pb2.ExecuteRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> Iterator[api_pb2.ExecuteResponse]:
        return self._execute_iterator(req, extra_headers, timeout_seconds)

    def _execute_iterator(
        self, req: api_pb2.ExecuteRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> Iterator[api_pb2.ExecuteResponse]:
        stream_output = self.call_execute(req, extra_headers)
        err = stream_output.error()
        if err is not None:
            raise err
        yield from stream_output
        err = stream_output.error()
        if err is not None:
            raise err

    def call_execute(
        self, req: api_pb2.ExecuteRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> StreamOutput[api_pb2.ExecuteResponse]:
        """Low-level method to call Execute, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.ExecutionService/Execute"
        return self._connect_client.call_server_streaming(
            url, req, api_pb2.ExecuteResponse, extra_headers, timeout_seconds
        )


class AsyncExecutionServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    def execute(
        self, req: api_pb2.ExecuteRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncIterator[api_pb2.ExecuteResponse]:
        return self._execute_iterator(req, extra_headers, timeout_seconds)

    async def _execute_iterator(
        self, req: api_pb2.ExecuteRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncIterator[api_pb2.ExecuteResponse]:
        stream_output = await self.call_execute(req, extra_headers)
        err = stream_output.error()
        if err is not None:
            raise err
        async with stream_output as stream:
            async for response in stream:
                yield response
            err = stream.error()
            if err is not None:
                raise err

    async def call_execute(
        self, req: api_pb2.ExecuteRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> AsyncStreamOutput[api_pb2.ExecuteResponse]:
        """Low-level method to call Execute, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.ExecutionService/Execute"
        return await self._connect_client.call_server_streaming(
            url, req, api_pb2.ExecuteResponse, extra_headers, timeout_seconds
        )


@typing.runtime_checkable
class ExecutionServiceProtocol(typing.Protocol):
    def execute(self, req: ClientRequest[api_pb2.ExecuteRequest]) -> ServerStream[api_pb2.ExecuteResponse]:
        ...

EXECUTION_SERVICE_PATH_PREFIX = "/sandboxagent.ExecutionService"

def wsgi_execution_service(implementation: ExecutionServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_server_streaming_rpc("/sandboxagent.ExecutionService/Execute", implementation.execute, api_pb2.ExecuteRequest)
    return app

class ContextServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create_context(
        self, req: api_pb2.CreateContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.Context]:
        """Low-level method to call CreateContext, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.ContextService/CreateContext"
        return self._connect_client.call_unary(url, req, api_pb2.Context,extra_headers, timeout_seconds)


    def create_context(
        self, req: api_pb2.CreateContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.Context:
        response = self.call_create_context(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_destroy_context(
        self, req: api_pb2.DestroyContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.DestroyContextResponse]:
        """Low-level method to call DestroyContext, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.ContextService/DestroyContext"
        return self._connect_client.call_unary(url, req, api_pb2.DestroyContextResponse,extra_headers, timeout_seconds)


    def destroy_context(
        self, req: api_pb2.DestroyContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.DestroyContextResponse:
        response = self.call_destroy_context(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncContextServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create_context(
        self, req: api_pb2.CreateContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.Context]:
        """Low-level method to call CreateContext, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.ContextService/CreateContext"
        return await self._connect_client.call_unary(url, req, api_pb2.Context,extra_headers, timeout_seconds)

    async def create_context(
        self, req: api_pb2.CreateContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.Context:
        response = await self.call_create_context(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_destroy_context(
        self, req: api_pb2.DestroyContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[api_pb2.DestroyContextResponse]:
        """Low-level method to call DestroyContext, granting access to errors and metadata"""
        url = self.base_url + "/sandboxagent.ContextService/DestroyContext"
        return await self._connect_client.call_unary(url, req, api_pb2.DestroyContextResponse,extra_headers, timeout_seconds)

    async def destroy_context(
        self, req: api_pb2.DestroyContextRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> api_pb2.DestroyContextResponse:
        response = await self.call_destroy_context(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class ContextServiceProtocol(typing.Protocol):
    def create_context(self, req: ClientRequest[api_pb2.CreateContextRequest]) -> ServerResponse[api_pb2.Context]:
        ...
    def destroy_context(self, req: ClientRequest[api_pb2.DestroyContextRequest]) -> ServerResponse[api_pb2.DestroyContextResponse]:
        ...

CONTEXT_SERVICE_PATH_PREFIX = "/sandboxagent.ContextService"

def wsgi_context_service(implementation: ContextServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/sandboxagent.ContextService/CreateContext", implementation.create_context, api_pb2.CreateContextRequest)
    app.register_unary_rpc("/sandboxagent.ContextService/DestroyContext", implementation.destroy_context, api_pb2.DestroyContextRequest)
    return app
