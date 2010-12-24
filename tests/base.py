"""
Module providing backend independent mixin class. It requires that
InMemoryChangeset class is working properly at backend class.
"""
import vcs
import time
import datetime
import unittest2

from conf import SCM_TESTS, get_new_dir

from vcs.exceptions import EmptyRepositoryError
from vcs.exceptions import NodeAlreadyAddedError
from vcs.exceptions import NodeAlreadyExistsError
from vcs.exceptions import NodeAlreadyRemovedError
from vcs.exceptions import NodeAlreadyChangedError
from vcs.exceptions import NodeDoesNotExistError
from vcs.exceptions import NodeNotChangedError
from vcs.nodes import FileNode


class BackendTestMixin(object):
    """
    This is a backend independent test case class which should be created
    with ``type`` method.

    It is required to set following attributes at subclass:

    - ``backend_alias``: alias of used backend (see ``vcs.BACKENDS``)
    - ``repo_path``: path to the repository which would be created for set of
      tests
    """

    def get_backend(self):
        return vcs.get_backend(self.backend_alias)

    def _get_commits(self):
        commits = [
            {
                'message': 'Initial commit',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'added': [
                    FileNode('foobar', content='Foobar'),
                    FileNode('foobar2', content='Foobar II'),
                    FileNode('foo/bar/baz', content='baz here!'),
                ],
            },
            {
                'message': 'Changes...',
                'author': 'Jane Doe <jane.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 21),
                'added': [
                    FileNode('some/new.txt', content='news...'),
                ],
                'changed': [
                    FileNode('foobar', 'Foobar I'),
                ],
                'removed': [],
            },
        ]
        return commits

    def setUp(self):
        Backend = self.get_backend()
        self.repo_path = get_new_dir(str(time.time()))
        self.repo = Backend(self.repo_path, create=True)
        self.imc = self.repo.in_memory_changeset

        for commit in self._get_commits():
            for node in commit.get('added', []):
                print node
                self.imc.add(FileNode(node.path, content=node.content))
            for node in commit.get('changed', []):
                self.imc.change(FileNode(node.path, content=node.content))
            for node in commit.get('removed', []):
                self.imc.remove(FileNode(node.path))
            self.imc.commit(message=commit['message'], author=commit['author'])

    def test_base(self):
        pass

# For each backend create test case class
for alias in SCM_TESTS:
    attrs = {
        'backend_alias': alias,
    }
    cls_name = ''.join(('%s base backend test' % alias).title().split())
    bases = (BackendTestMixin, unittest2.TestCase)
    globals()[cls_name] = type(cls_name, bases, attrs)


if __name__ == '__main__':
    unittest2.main()
