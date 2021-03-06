import traceback
from decimal import Decimal

from ..constants.identity import IdentityDelimeter
from ..constants.method import TagName, MetaStatusChoice
from ..runtime.method_executor import MethodExecutor
from ..runtime.utils.names import find_yaml_files


class NamespaceRoot(object):
    def __init__(self, identity, file_path, actions, contained_namespaces, unit_test_loading_bypass=False):
        self._identity = identity
        self._path = '/'.join(file_path.split('/')[:-1])
        self._domain = None
        self._actions = dict()
        self._action_functions = actions
        self._contained_namespaces = contained_namespaces
        self._yaml_documents = dict()
        if not unit_test_loading_bypass:
            self.load_yaml_documents()
            self.load_actions()

    @property
    def identity(self):
        return self._identity

    @property
    def path(self):
        return self._path

    @property
    def domain(self):
        return self._domain

    @property
    def actions(self):
        return self._actions

    @property
    def contained_namespaces(self):
        return self._contained_namespaces

    @property
    def yaml_documents(self):
        return self._yaml_documents

    def set_domain(self, domain):
        self._domain = domain

    def load_actions(self):
        from .store import NameStore
        for action in self._action_functions:
            action_versions = NameStore.pop_action_versions(action.__name__)
            for action_identity, fx in action_versions:
                self._actions[action_identity] = fx

    def load_yaml_documents(self):
        from ..method.loading import load_method
        semantic_versions = dict()
        for document_path in find_yaml_files(self):
            with open(document_path, 'r') as document:
                try:
                    yaml_document = load_method(document.read())
                    # todo: WFS-16 - validate yaml_document on load
                    identity_node = yaml_document[TagName.IDENTITY]
                    document_identity = identity_node.constructed
                    numeric_version = Decimal(identity_node.deconstructed[TagName.version].value)
                    semantic_version = identity_node.deconstructed[TagName.status].value
                    if numeric_version > semantic_versions.get(semantic_version, 0):
                        semantic_versions[semantic_version] = numeric_version
                        default_identity = f'{document_identity.split(IdentityDelimeter.VERSION)[0]}'
                        semantic_identity = f'{default_identity}{IdentityDelimeter.VERSION}{semantic_version}'
                        self._yaml_documents[semantic_identity] = yaml_document
                        if semantic_version == MetaStatusChoice.PRODUCTION:
                            # latest production version is also default version
                            self._yaml_documents[default_identity] = yaml_document
                    self._yaml_documents[document_identity] = yaml_document
                except Exception as err:
                    raise RuntimeError(f'While loading document {document_path}:\n\t{traceback.format_exc()}')

    def get_method(self, identity):
        if identity in self.yaml_documents:
            return MethodExecutor(identity, self.yaml_documents[identity], self)
        else:
            return self.domain.get_method(identity)
        raise RuntimeError(f'Method {identity} could not be resolved by namespace_root {self.identity}')


    def get_action(self, identity):
        if identity in self.actions:
            return self.actions[identity]
        else:
            return self.domain.get_action(identity)
        raise RuntimeError(f'Action {identity} could not be resolved by namespace_root {self.identity}')
