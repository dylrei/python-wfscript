from .data import InputTag, StateTag
from .executors import ActionTag, MethodTag
from ..constants.loading import TagName


constructor_for_tag = {
    TagName.Action: ActionTag,
    TagName.Method: MethodTag,
    TagName.Input: InputTag,
    TagName.State: StateTag
}