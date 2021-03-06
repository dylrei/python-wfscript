import os

from . import hello_world
from ....runtime.store import NameStore

content_root_path = os.path.sep.join(__file__.split(os.path.sep)[:-1])

content_root_module = __name__

loading_namespace_root = NameStore.namespace_root(
    identity=__name__,
    file_path=__file__,
    actions=[hello_world],
    contained_namespaces=[],
    unit_test_loading_bypass=True
)
