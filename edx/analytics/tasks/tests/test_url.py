import luigi
import luigi.format
import luigi.hdfs
import luigi.s3

from edx.analytics.tasks import url
from edx.analytics.tasks.tests import unittest


class TargetFromUrlTestCase(unittest.TestCase):

    def test_hdfs_scheme(self):
        for test_url in ['s3://foo/bar', 'hdfs://foo/bar', 's3n://foo/bar']:
            target = url.get_target_from_url(test_url)
            self.assertIsInstance(target, luigi.hdfs.HdfsTarget)
            self.assertEquals(target.path, test_url)

    def test_file_scheme(self):
        path = '/foo/bar'
        for test_url in [path, 'file://' + path]:
            target = url.get_target_from_url(test_url)
            self.assertIsInstance(target, luigi.LocalTarget)
            self.assertEquals(target.path, path)

    def test_s3_https_scheme(self):
        test_url = 's3+https://foo/bar'
        target = url.get_target_from_url(test_url)
        self.assertIsInstance(target, luigi.s3.S3Target)
        self.assertEquals(target.path, test_url)

    def test_hdfs_directory(self):
        test_url = 's3://foo/bar/'
        target = url.get_target_from_url(test_url)
        self.assertIsInstance(target, luigi.hdfs.HdfsTarget)
        self.assertEquals(target.path, test_url)
        self.assertEquals(target.format, luigi.hdfs.PlainDir)

    def test_gzip_local_file(self):
        test_url = '/foo/bar.gz'
        target = url.get_target_from_url(test_url)
        self.assertIsInstance(target, luigi.LocalTarget)
        self.assertEquals(target.path, test_url)
        self.assertEquals(target.format, luigi.format.Gzip)


class UrlPathJoinTestCase(unittest.TestCase):

    def test_relative(self):
        self.assertEquals(url.url_path_join('s3://foo/bar', 'baz'), 's3://foo/bar/baz')

    def test_absolute(self):
        self.assertEquals(url.url_path_join('s3://foo/bar', '/baz'), 's3://foo/baz')

    def test_attempted_special_elements(self):
        self.assertEquals(url.url_path_join('s3://foo/bar', './baz'), 's3://foo/bar/./baz')
        self.assertEquals(url.url_path_join('s3://foo/bar', '../baz'), 's3://foo/bar/../baz')

    def test_no_path(self):
        self.assertEquals(url.url_path_join('s3://foo', 'baz'), 's3://foo/baz')

    def test_no_netloc(self):
        self.assertEquals(url.url_path_join('file:///foo/bar', 'baz'), 'file:///foo/bar/baz')

    def test_extra_separators(self):
        self.assertEquals(url.url_path_join('s3://foo/bar', '///baz'), 's3://foo///baz')
        self.assertEquals(url.url_path_join('s3://foo/bar', 'baz//bar'), 's3://foo/bar/baz//bar')

    def test_extra_separators(self):
        self.assertEquals(url.url_path_join('s3://foo/bar', '///baz'), 's3://foo///baz')

    @unittest.skip("Failing in Python 2.6 due to differences in urlparse")
    def test_query_string(self):
        self.assertEquals(url.url_path_join('s3://foo/bar?x=y', 'baz'), 's3://foo/bar/baz?x=y')

    def test_multiple_elements(self):
        self.assertEquals(url.url_path_join('s3://foo', 'bar', 'baz'), 's3://foo/bar/baz')
        self.assertEquals(url.url_path_join('s3://foo', 'bar/bing', 'baz'), 's3://foo/bar/bing/baz')