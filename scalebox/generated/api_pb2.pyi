import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILE_TYPE_UNSPECIFIED: _ClassVar[FileType]
    FILE_TYPE_FILE: _ClassVar[FileType]
    FILE_TYPE_DIRECTORY: _ClassVar[FileType]

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    EVENT_TYPE_CREATE: _ClassVar[EventType]
    EVENT_TYPE_WRITE: _ClassVar[EventType]
    EVENT_TYPE_REMOVE: _ClassVar[EventType]
    EVENT_TYPE_RENAME: _ClassVar[EventType]
    EVENT_TYPE_CHMOD: _ClassVar[EventType]

class Signal(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIGNAL_UNSPECIFIED: _ClassVar[Signal]
    SIGNAL_SIGTERM: _ClassVar[Signal]
    SIGNAL_SIGKILL: _ClassVar[Signal]
FILE_TYPE_UNSPECIFIED: FileType
FILE_TYPE_FILE: FileType
FILE_TYPE_DIRECTORY: FileType
EVENT_TYPE_UNSPECIFIED: EventType
EVENT_TYPE_CREATE: EventType
EVENT_TYPE_WRITE: EventType
EVENT_TYPE_REMOVE: EventType
EVENT_TYPE_RENAME: EventType
EVENT_TYPE_CHMOD: EventType
SIGNAL_UNSPECIFIED: Signal
SIGNAL_SIGTERM: Signal
SIGNAL_SIGKILL: Signal

class MoveRequest(_message.Message):
    __slots__ = ("source", "destination")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    source: str
    destination: str
    def __init__(self, source: _Optional[str] = ..., destination: _Optional[str] = ...) -> None: ...

class MoveResponse(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: EntryInfo
    def __init__(self, entry: _Optional[_Union[EntryInfo, _Mapping]] = ...) -> None: ...

class MakeDirRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class MakeDirResponse(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: EntryInfo
    def __init__(self, entry: _Optional[_Union[EntryInfo, _Mapping]] = ...) -> None: ...

class RemoveRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class RemoveResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class StatResponse(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: EntryInfo
    def __init__(self, entry: _Optional[_Union[EntryInfo, _Mapping]] = ...) -> None: ...

class EntryInfo(_message.Message):
    __slots__ = ("name", "type", "path", "size", "mode", "permissions", "owner", "group", "modified_time", "symlink_target")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_TIME_FIELD_NUMBER: _ClassVar[int]
    SYMLINK_TARGET_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: FileType
    path: str
    size: int
    mode: int
    permissions: str
    owner: str
    group: str
    modified_time: _timestamp_pb2.Timestamp
    symlink_target: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[FileType, str]] = ..., path: _Optional[str] = ..., size: _Optional[int] = ..., mode: _Optional[int] = ..., permissions: _Optional[str] = ..., owner: _Optional[str] = ..., group: _Optional[str] = ..., modified_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., symlink_target: _Optional[str] = ...) -> None: ...

class ListDirRequest(_message.Message):
    __slots__ = ("path", "depth")
    PATH_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    path: str
    depth: int
    def __init__(self, path: _Optional[str] = ..., depth: _Optional[int] = ...) -> None: ...

class ListDirResponse(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[EntryInfo]
    def __init__(self, entries: _Optional[_Iterable[_Union[EntryInfo, _Mapping]]] = ...) -> None: ...

class WatchDirRequest(_message.Message):
    __slots__ = ("path", "recursive")
    PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    path: str
    recursive: bool
    def __init__(self, path: _Optional[str] = ..., recursive: _Optional[bool] = ...) -> None: ...

class FilesystemEvent(_message.Message):
    __slots__ = ("name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: EventType
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[EventType, str]] = ...) -> None: ...

class WatchDirResponse(_message.Message):
    __slots__ = ("start", "filesystem", "keepalive")
    class StartEvent(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class KeepAlive(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    START_FIELD_NUMBER: _ClassVar[int]
    FILESYSTEM_FIELD_NUMBER: _ClassVar[int]
    KEEPALIVE_FIELD_NUMBER: _ClassVar[int]
    start: WatchDirResponse.StartEvent
    filesystem: FilesystemEvent
    keepalive: WatchDirResponse.KeepAlive
    def __init__(self, start: _Optional[_Union[WatchDirResponse.StartEvent, _Mapping]] = ..., filesystem: _Optional[_Union[FilesystemEvent, _Mapping]] = ..., keepalive: _Optional[_Union[WatchDirResponse.KeepAlive, _Mapping]] = ...) -> None: ...

class CreateWatcherRequest(_message.Message):
    __slots__ = ("path", "recursive")
    PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    path: str
    recursive: bool
    def __init__(self, path: _Optional[str] = ..., recursive: _Optional[bool] = ...) -> None: ...

class CreateWatcherResponse(_message.Message):
    __slots__ = ("watcher_id",)
    WATCHER_ID_FIELD_NUMBER: _ClassVar[int]
    watcher_id: str
    def __init__(self, watcher_id: _Optional[str] = ...) -> None: ...

class GetWatcherEventsRequest(_message.Message):
    __slots__ = ("watcher_id",)
    WATCHER_ID_FIELD_NUMBER: _ClassVar[int]
    watcher_id: str
    def __init__(self, watcher_id: _Optional[str] = ...) -> None: ...

class GetWatcherEventsResponse(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[FilesystemEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[FilesystemEvent, _Mapping]]] = ...) -> None: ...

class RemoveWatcherRequest(_message.Message):
    __slots__ = ("watcher_id",)
    WATCHER_ID_FIELD_NUMBER: _ClassVar[int]
    watcher_id: str
    def __init__(self, watcher_id: _Optional[str] = ...) -> None: ...

class RemoveWatcherResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PTY(_message.Message):
    __slots__ = ("size",)
    class Size(_message.Message):
        __slots__ = ("cols", "rows")
        COLS_FIELD_NUMBER: _ClassVar[int]
        ROWS_FIELD_NUMBER: _ClassVar[int]
        cols: int
        rows: int
        def __init__(self, cols: _Optional[int] = ..., rows: _Optional[int] = ...) -> None: ...
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: PTY.Size
    def __init__(self, size: _Optional[_Union[PTY.Size, _Mapping]] = ...) -> None: ...

class ProcessConfig(_message.Message):
    __slots__ = ("cmd", "args", "envs", "cwd")
    class EnvsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CMD_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    ENVS_FIELD_NUMBER: _ClassVar[int]
    CWD_FIELD_NUMBER: _ClassVar[int]
    cmd: str
    args: _containers.RepeatedScalarFieldContainer[str]
    envs: _containers.ScalarMap[str, str]
    cwd: str
    def __init__(self, cmd: _Optional[str] = ..., args: _Optional[_Iterable[str]] = ..., envs: _Optional[_Mapping[str, str]] = ..., cwd: _Optional[str] = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProcessInfo(_message.Message):
    __slots__ = ("config", "pid", "tag")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    config: ProcessConfig
    pid: int
    tag: str
    def __init__(self, config: _Optional[_Union[ProcessConfig, _Mapping]] = ..., pid: _Optional[int] = ..., tag: _Optional[str] = ...) -> None: ...

class ListResponse(_message.Message):
    __slots__ = ("processes",)
    PROCESSES_FIELD_NUMBER: _ClassVar[int]
    processes: _containers.RepeatedCompositeFieldContainer[ProcessInfo]
    def __init__(self, processes: _Optional[_Iterable[_Union[ProcessInfo, _Mapping]]] = ...) -> None: ...

class StartRequest(_message.Message):
    __slots__ = ("process", "pty", "tag")
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    PTY_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    process: ProcessConfig
    pty: PTY
    tag: str
    def __init__(self, process: _Optional[_Union[ProcessConfig, _Mapping]] = ..., pty: _Optional[_Union[PTY, _Mapping]] = ..., tag: _Optional[str] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("process", "pty")
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    PTY_FIELD_NUMBER: _ClassVar[int]
    process: ProcessSelector
    pty: PTY
    def __init__(self, process: _Optional[_Union[ProcessSelector, _Mapping]] = ..., pty: _Optional[_Union[PTY, _Mapping]] = ...) -> None: ...

class UpdateResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProcessEvent(_message.Message):
    __slots__ = ("start", "data", "end", "keepalive")
    class StartEvent(_message.Message):
        __slots__ = ("pid",)
        PID_FIELD_NUMBER: _ClassVar[int]
        pid: int
        def __init__(self, pid: _Optional[int] = ...) -> None: ...
    class DataEvent(_message.Message):
        __slots__ = ("stdout", "stderr", "pty")
        STDOUT_FIELD_NUMBER: _ClassVar[int]
        STDERR_FIELD_NUMBER: _ClassVar[int]
        PTY_FIELD_NUMBER: _ClassVar[int]
        stdout: bytes
        stderr: bytes
        pty: bytes
        def __init__(self, stdout: _Optional[bytes] = ..., stderr: _Optional[bytes] = ..., pty: _Optional[bytes] = ...) -> None: ...
    class EndEvent(_message.Message):
        __slots__ = ("exit_code", "exited", "status", "error")
        EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
        EXITED_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        ERROR_FIELD_NUMBER: _ClassVar[int]
        exit_code: int
        exited: bool
        status: str
        error: str
        def __init__(self, exit_code: _Optional[int] = ..., exited: _Optional[bool] = ..., status: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...
    class KeepAlive(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    START_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    KEEPALIVE_FIELD_NUMBER: _ClassVar[int]
    start: ProcessEvent.StartEvent
    data: ProcessEvent.DataEvent
    end: ProcessEvent.EndEvent
    keepalive: ProcessEvent.KeepAlive
    def __init__(self, start: _Optional[_Union[ProcessEvent.StartEvent, _Mapping]] = ..., data: _Optional[_Union[ProcessEvent.DataEvent, _Mapping]] = ..., end: _Optional[_Union[ProcessEvent.EndEvent, _Mapping]] = ..., keepalive: _Optional[_Union[ProcessEvent.KeepAlive, _Mapping]] = ...) -> None: ...

class StartResponse(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: ProcessEvent
    def __init__(self, event: _Optional[_Union[ProcessEvent, _Mapping]] = ...) -> None: ...

class ConnectResponse(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: ProcessEvent
    def __init__(self, event: _Optional[_Union[ProcessEvent, _Mapping]] = ...) -> None: ...

class SendInputRequest(_message.Message):
    __slots__ = ("process", "input")
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    process: ProcessSelector
    input: ProcessInput
    def __init__(self, process: _Optional[_Union[ProcessSelector, _Mapping]] = ..., input: _Optional[_Union[ProcessInput, _Mapping]] = ...) -> None: ...

class SendInputResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProcessInput(_message.Message):
    __slots__ = ("stdin", "pty")
    STDIN_FIELD_NUMBER: _ClassVar[int]
    PTY_FIELD_NUMBER: _ClassVar[int]
    stdin: bytes
    pty: bytes
    def __init__(self, stdin: _Optional[bytes] = ..., pty: _Optional[bytes] = ...) -> None: ...

class StreamInputRequest(_message.Message):
    __slots__ = ("start", "data", "keepalive")
    class StartEvent(_message.Message):
        __slots__ = ("process",)
        PROCESS_FIELD_NUMBER: _ClassVar[int]
        process: ProcessSelector
        def __init__(self, process: _Optional[_Union[ProcessSelector, _Mapping]] = ...) -> None: ...
    class DataEvent(_message.Message):
        __slots__ = ("input",)
        INPUT_FIELD_NUMBER: _ClassVar[int]
        input: ProcessInput
        def __init__(self, input: _Optional[_Union[ProcessInput, _Mapping]] = ...) -> None: ...
    class KeepAlive(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    START_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    KEEPALIVE_FIELD_NUMBER: _ClassVar[int]
    start: StreamInputRequest.StartEvent
    data: StreamInputRequest.DataEvent
    keepalive: StreamInputRequest.KeepAlive
    def __init__(self, start: _Optional[_Union[StreamInputRequest.StartEvent, _Mapping]] = ..., data: _Optional[_Union[StreamInputRequest.DataEvent, _Mapping]] = ..., keepalive: _Optional[_Union[StreamInputRequest.KeepAlive, _Mapping]] = ...) -> None: ...

class StreamInputResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SendSignalRequest(_message.Message):
    __slots__ = ("process", "signal")
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    SIGNAL_FIELD_NUMBER: _ClassVar[int]
    process: ProcessSelector
    signal: Signal
    def __init__(self, process: _Optional[_Union[ProcessSelector, _Mapping]] = ..., signal: _Optional[_Union[Signal, str]] = ...) -> None: ...

class SendSignalResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ConnectRequest(_message.Message):
    __slots__ = ("process",)
    PROCESS_FIELD_NUMBER: _ClassVar[int]
    process: ProcessSelector
    def __init__(self, process: _Optional[_Union[ProcessSelector, _Mapping]] = ...) -> None: ...

class ProcessSelector(_message.Message):
    __slots__ = ("pid", "tag")
    PID_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    pid: int
    tag: str
    def __init__(self, pid: _Optional[int] = ..., tag: _Optional[str] = ...) -> None: ...

class ExecuteRequest(_message.Message):
    __slots__ = ("context_id", "code", "language", "env_vars")
    class EnvVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONTEXT_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    context_id: str
    code: str
    language: str
    env_vars: _containers.ScalarMap[str, str]
    def __init__(self, context_id: _Optional[str] = ..., code: _Optional[str] = ..., language: _Optional[str] = ..., env_vars: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ExecuteResponse(_message.Message):
    __slots__ = ("stdout", "stderr", "result", "error")
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    STDERR_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    stdout: Output
    stderr: Output
    result: Result
    error: Error
    def __init__(self, stdout: _Optional[_Union[Output, _Mapping]] = ..., stderr: _Optional[_Union[Output, _Mapping]] = ..., result: _Optional[_Union[Result, _Mapping]] = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class Output(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ("exit_code", "started_at", "finished_at", "text", "html", "markdown", "svg", "png", "jpeg", "pdf", "latex", "json", "javascript", "data", "chart", "execution_count", "is_main_result", "extra")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    EXIT_CODE_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    HTML_FIELD_NUMBER: _ClassVar[int]
    MARKDOWN_FIELD_NUMBER: _ClassVar[int]
    SVG_FIELD_NUMBER: _ClassVar[int]
    PNG_FIELD_NUMBER: _ClassVar[int]
    JPEG_FIELD_NUMBER: _ClassVar[int]
    PDF_FIELD_NUMBER: _ClassVar[int]
    LATEX_FIELD_NUMBER: _ClassVar[int]
    JSON_FIELD_NUMBER: _ClassVar[int]
    JAVASCRIPT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHART_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_COUNT_FIELD_NUMBER: _ClassVar[int]
    IS_MAIN_RESULT_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    exit_code: int
    started_at: _timestamp_pb2.Timestamp
    finished_at: _timestamp_pb2.Timestamp
    text: str
    html: str
    markdown: str
    svg: str
    png: str
    jpeg: str
    pdf: str
    latex: str
    json: str
    javascript: str
    data: str
    chart: Chart
    execution_count: int
    is_main_result: bool
    extra: _containers.ScalarMap[str, str]
    def __init__(self, exit_code: _Optional[int] = ..., started_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., finished_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., text: _Optional[str] = ..., html: _Optional[str] = ..., markdown: _Optional[str] = ..., svg: _Optional[str] = ..., png: _Optional[str] = ..., jpeg: _Optional[str] = ..., pdf: _Optional[str] = ..., latex: _Optional[str] = ..., json: _Optional[str] = ..., javascript: _Optional[str] = ..., data: _Optional[str] = ..., chart: _Optional[_Union[Chart, _Mapping]] = ..., execution_count: _Optional[int] = ..., is_main_result: _Optional[bool] = ..., extra: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("name", "value", "traceback")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TRACEBACK_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    traceback: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., traceback: _Optional[str] = ...) -> None: ...

class Chart(_message.Message):
    __slots__ = ("type", "title", "elements", "extra")
    class ExtraEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    type: str
    title: str
    elements: _containers.RepeatedCompositeFieldContainer[ChartElement]
    extra: _containers.ScalarMap[str, str]
    def __init__(self, type: _Optional[str] = ..., title: _Optional[str] = ..., elements: _Optional[_Iterable[_Union[ChartElement, _Mapping]]] = ..., extra: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ChartElement(_message.Message):
    __slots__ = ("point_data", "bar_data", "pie_data", "box_whisker_data", "nested_chart")
    POINT_DATA_FIELD_NUMBER: _ClassVar[int]
    BAR_DATA_FIELD_NUMBER: _ClassVar[int]
    PIE_DATA_FIELD_NUMBER: _ClassVar[int]
    BOX_WHISKER_DATA_FIELD_NUMBER: _ClassVar[int]
    NESTED_CHART_FIELD_NUMBER: _ClassVar[int]
    point_data: PointData
    bar_data: BarData
    pie_data: PieData
    box_whisker_data: BoxAndWhiskerData
    nested_chart: Chart
    def __init__(self, point_data: _Optional[_Union[PointData, _Mapping]] = ..., bar_data: _Optional[_Union[BarData, _Mapping]] = ..., pie_data: _Optional[_Union[PieData, _Mapping]] = ..., box_whisker_data: _Optional[_Union[BoxAndWhiskerData, _Mapping]] = ..., nested_chart: _Optional[_Union[Chart, _Mapping]] = ...) -> None: ...

class PointData(_message.Message):
    __slots__ = ("label", "points")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    label: str
    points: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, label: _Optional[str] = ..., points: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ("x_str", "x_num", "y_str", "y_num")
    X_STR_FIELD_NUMBER: _ClassVar[int]
    X_NUM_FIELD_NUMBER: _ClassVar[int]
    Y_STR_FIELD_NUMBER: _ClassVar[int]
    Y_NUM_FIELD_NUMBER: _ClassVar[int]
    x_str: str
    x_num: float
    y_str: str
    y_num: float
    def __init__(self, x_str: _Optional[str] = ..., x_num: _Optional[float] = ..., y_str: _Optional[str] = ..., y_num: _Optional[float] = ...) -> None: ...

class BarData(_message.Message):
    __slots__ = ("label", "group", "value")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    label: str
    group: str
    value: str
    def __init__(self, label: _Optional[str] = ..., group: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class PieData(_message.Message):
    __slots__ = ("label", "angle", "radius")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    ANGLE_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    label: str
    angle: float
    radius: float
    def __init__(self, label: _Optional[str] = ..., angle: _Optional[float] = ..., radius: _Optional[float] = ...) -> None: ...

class BoxAndWhiskerData(_message.Message):
    __slots__ = ("label", "min", "first_quartile", "median", "third_quartile", "max", "outliers")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    FIRST_QUARTILE_FIELD_NUMBER: _ClassVar[int]
    MEDIAN_FIELD_NUMBER: _ClassVar[int]
    THIRD_QUARTILE_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    OUTLIERS_FIELD_NUMBER: _ClassVar[int]
    label: str
    min: float
    first_quartile: float
    median: float
    third_quartile: float
    max: float
    outliers: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, label: _Optional[str] = ..., min: _Optional[float] = ..., first_quartile: _Optional[float] = ..., median: _Optional[float] = ..., third_quartile: _Optional[float] = ..., max: _Optional[float] = ..., outliers: _Optional[_Iterable[float]] = ...) -> None: ...

class Chart2D(_message.Message):
    __slots__ = ("x_label", "y_label", "x_unit", "y_unit", "chart")
    X_LABEL_FIELD_NUMBER: _ClassVar[int]
    Y_LABEL_FIELD_NUMBER: _ClassVar[int]
    X_UNIT_FIELD_NUMBER: _ClassVar[int]
    Y_UNIT_FIELD_NUMBER: _ClassVar[int]
    CHART_FIELD_NUMBER: _ClassVar[int]
    x_label: str
    y_label: str
    x_unit: str
    y_unit: str
    chart: Chart
    def __init__(self, x_label: _Optional[str] = ..., y_label: _Optional[str] = ..., x_unit: _Optional[str] = ..., y_unit: _Optional[str] = ..., chart: _Optional[_Union[Chart, _Mapping]] = ...) -> None: ...

class PointChart(_message.Message):
    __slots__ = ("x_ticks", "x_tick_labels", "x_scale", "y_ticks", "y_tick_labels", "y_scale", "chart_2d")
    X_TICKS_FIELD_NUMBER: _ClassVar[int]
    X_TICK_LABELS_FIELD_NUMBER: _ClassVar[int]
    X_SCALE_FIELD_NUMBER: _ClassVar[int]
    Y_TICKS_FIELD_NUMBER: _ClassVar[int]
    Y_TICK_LABELS_FIELD_NUMBER: _ClassVar[int]
    Y_SCALE_FIELD_NUMBER: _ClassVar[int]
    CHART_2D_FIELD_NUMBER: _ClassVar[int]
    x_ticks: _containers.RepeatedScalarFieldContainer[str]
    x_tick_labels: _containers.RepeatedScalarFieldContainer[str]
    x_scale: str
    y_ticks: _containers.RepeatedScalarFieldContainer[str]
    y_tick_labels: _containers.RepeatedScalarFieldContainer[str]
    y_scale: str
    chart_2d: Chart2D
    def __init__(self, x_ticks: _Optional[_Iterable[str]] = ..., x_tick_labels: _Optional[_Iterable[str]] = ..., x_scale: _Optional[str] = ..., y_ticks: _Optional[_Iterable[str]] = ..., y_tick_labels: _Optional[_Iterable[str]] = ..., y_scale: _Optional[str] = ..., chart_2d: _Optional[_Union[Chart2D, _Mapping]] = ...) -> None: ...

class CreateContextRequest(_message.Message):
    __slots__ = ("language", "cwd")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    CWD_FIELD_NUMBER: _ClassVar[int]
    language: str
    cwd: str
    def __init__(self, language: _Optional[str] = ..., cwd: _Optional[str] = ...) -> None: ...

class Context(_message.Message):
    __slots__ = ("id", "language", "cwd", "created_at", "env_vars")
    class EnvVarsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    CWD_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    id: str
    language: str
    cwd: str
    created_at: _timestamp_pb2.Timestamp
    env_vars: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., language: _Optional[str] = ..., cwd: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., env_vars: _Optional[_Mapping[str, str]] = ...) -> None: ...

class DestroyContextRequest(_message.Message):
    __slots__ = ("context_id",)
    CONTEXT_ID_FIELD_NUMBER: _ClassVar[int]
    context_id: str
    def __init__(self, context_id: _Optional[str] = ...) -> None: ...

class DestroyContextResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: _Optional[bool] = ...) -> None: ...
