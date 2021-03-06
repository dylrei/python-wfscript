from datetime import timezone, datetime

from ..constants.payload import PayloadKey


class ExecutorReturn(object):
    def __init__(self, result, state=None):
        self._result = result
        self._state = state

    @property
    def result(self):
        return self._result

    @property
    def resume(self):
        return dict()

    def render(self):
        return {
            PayloadKey.RESULT: self.result,
            PayloadKey.RESUME: self.resume,
            PayloadKey.TIMESTAMP: datetime.now(tz=timezone.utc).isoformat(),
        }


class MethodReturn(ExecutorReturn):
    pass

class StepReturn(MethodReturn):
    _method = None
    _step = None

    @property
    def state(self):
        return self._state

    @property
    def resume(self):
        return {
            PayloadKey.METHOD: self._method,
            PayloadKey.STEP: self._step
        } if self._step else {}

    def add_step_resume_info(self, method, step):
        self._method = method
        self._step = step

    def set_result(self, result):
        self._result = result


class ActionReturn(ExecutorReturn):
    pass


class TicketReturn(ExecutorReturn):
    pass
