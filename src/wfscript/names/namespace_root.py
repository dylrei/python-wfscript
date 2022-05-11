from ..constants.identity import IdentityDelimeter
from ..constants.loading import TagName, MetaSectionKey, MetaStatusChoice
from ..executors.method import MethodExecutor
from ..executors.validator import ValidatorExecutor
from ..utils.identity import construct_identity
from ..utils.names import find_yaml_files


class NamespaceRoot(object):
    def __init__(self, identity, file_path, actions, contained_namespaces, unit_test_loading_bypass=False):
        self._identity = identity
        self._path = '/'.join(file_path.split('/')[:-1])
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
        from ..loading.loader import load_yaml_document
        semantic_versions = dict()
        for document_path in find_yaml_files(self):
            with open(document_path, 'r') as document:
                yaml_document = load_yaml_document(document.read())
                # todo: WFS-16 - validate yaml_document on load
                document_identity = construct_identity(yaml_document[TagName.META].value)
                numeric_version = yaml_document[TagName.META].value[MetaSectionKey.VERSION]
                semantic_version = yaml_document[TagName.META].value[MetaSectionKey.STATUS]
                if numeric_version > semantic_versions.get(semantic_version, 0):
                    semantic_versions[semantic_version] = numeric_version
                    default_identity = f'{document_identity.split(IdentityDelimeter.VERSION)[0]}'
                    semantic_identity = f'{default_identity}{IdentityDelimeter.VERSION}{semantic_version}'
                    self._yaml_documents[semantic_identity] = yaml_document
                    if semantic_version == MetaStatusChoice.PRODUCTION:
                        # latest production version is also default version
                        self._yaml_documents[default_identity] = yaml_document
                self._yaml_documents[document_identity] = yaml_document

    def load_actions(self):
        from .store import NameStore
        for action in self._action_functions:
            action_versions = NameStore.pop_action_versions(action.__name__)
            for action_identity, fx in action_versions:
                self._actions[action_identity] = fx

    def get_action(self, identity):
        if identity in self.actions:
            return self.actions[identity]