import libcloud
from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver

import os
import sys


class ArkivverketObjectStorage:
    """
    ArkivverketObjectStorage - Simple object storage API for The National Archieves of Norway.
    The goal is to abstract the details and provide a super-simple API towards various object
    storage solutions.

    Currently the API is implemented using Apache Libcloud and will only support a verified subset
    of Libcloud.

    The API is not meant for use outside the National Archieves.

    Configuration is done using enviroment variables. The following variables are used:
     - OBJECTSTORE Which driver - (gcs|s3)
     For GCS:
      - GOOGLE_ACCOUNT - the service account for GCS.
      - AUTH_TOKEN - Path to the JSON file containing the auth token for GCS. Typically a k8s secret.
     For S3 (not implmented yet)
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY

    Attributes
    ----------
    driver : object
        low level driver from libcloud.

    Methods
    -------
    The object returned has the following methods:

    contructor()
        reads OBJECTSTORE and likely other vars and configures the object.
    download_file(container, name, file)
        downloads a file, returns success or not
    download_stream(container, name)
        opens a stream to a file, returns a file-like object
    upload_file(container, name, file)
        uploads a local file to a container
    upload_stream(container, name, fileobj)
        uploads the contents of a file-like object to the cloud
    delete(container, name)
        deletes the object from the object storge.
    list_content(container)
        list the objects names in the given container
    """

    def __init__(self):
        driver = os.getenv('OBJECTSTORE')
        if (driver == 'gcs'):
            cls = get_driver(Provider.GOOGLE_STORAGE)
            self.driver = cls(os.getenv('GOOGLE_ACCOUNT'),
                              os.getenv('AUTH_TOKEN'),
                              project='mottak2')

        elif (driver == 's3'):
            # connect to AWS here.
            self.driver = driver
        else:
            raise Exception('Unknown storage provider')

    def _get_container(self, container):
        """ Return an container based on name"""
        container = self.driver.get_container(container_name=container)
        return container

    def get_size(self, container, name):
        """Get the size of a file/object in the objectstore

        Parameters
        ----------
        container : str
            name of the container
        name : str
            name of the object

        returns the size in bytes
        """
        obj = self.driver.get_object(
            container_name=container, object_name=name)

        return obj.size

    def download_file(self, container, name, file):
        """Download file to local filesystem from objectstore

        Parameters
        ----------
        container : str
            name of the container
        name : str
            name of the object
        file : str
            target path of the file to be downloaded

        """
        obj = self.driver.get_object(container_name=container,
                                     object_name=name)
        obj.download(file, overwrite_existing=True)

    def download_stream(self, container, name, chunk_size=8192):
        """Returns a stream (iterator) that delivers the object in chunks.

        Parameters
        ----------
        container : str
            name of the container
        name : str
            name of the object
        """
        obj = self.driver.get_object(container_name=container,
                                     object_name=name)
        stream = self.driver.download_object_as_stream(
            obj, chunk_size=chunk_size)
        return stream
        # return obj.as_stream(chunk_size=chunk_size)

    def upload_file(self, container, name, file):
        """Upload a local file to objectstore

        Parameters
        ----------
        container : str
            name of the container
        name : str
            name of the object
        file : str
            target path of the file to be downloaded

        """

        container = self._get_container(container)
        obj = self.driver.upload_object(file_path=file,
                                        container=container,
                                        object_name=name)
        return obj

    def upload_stream(self, container, name, iterator):
        print(f"Uploading stream {iterator} into {container} / {name}")
        container = self._get_container(container)
        return container.upload_object_via_stream(iterator=iterator, object_name=name)

    def delete(self, container, name):
        ret = False
        try:
            obj = self.driver.get_object(container_name=container,
                                         object_name=name)
            ret = obj.delete
        except libcloud.storage.types.ObjectDoesNotExistError:
            ret = False
        return ret

    def list_container(self, container):
        container = self._get_container(container)
        return list(map(lambda x: x.name, container.list_objects()))


class MakeIterIntoFile:
    """
    Turn an iterator into a READ ONLY file like object. Used to interface
    with the tarfile lib when dealing with streamed data.
    """

    def __init__(self, it, decode=False):
        self.it = iter(it)  # should throw exception if not iter
        self.offset = 0
        self.is_open = True
        self.decode = decode
        self.eof = False
        self.remainder = b''
        self.next_chunk = b''

    def _grow_chunk(self):
        self.next_chunk = self.next_chunk + self.it.__next__()

    def read(self, amount=0):
        if (self.eof):  # At EOF,
            return b''
        if not self.is_open:  # Return a short read. Wrong?
            return b''

        while (len(self.next_chunk) < amount):
            try:
                self._grow_chunk()
            except StopIteration: # Exhausted the file.
                break

        if (len(self.next_chunk) < amount):
            self.eof = True

            self.offset += len(self.next_chunk)
            return self.next_chunk
        
        # We got more data then the caller asked for. Chop off some data so tarfile is happy.
        ret = self.next_chunk[:amount]
        self.next_chunk = self.next_chunk[amount:]
        
        self.offset += len(ret)
        return ret

    def close(self):
        self.is_open = False
        self.next_chunk = None
        self.remainder = None
        return True

    def tell(self):
        return self.offset
        


class TarfileIterator:
    """
    Creates an iteratable object from a tarfile.
    """

    def __init__(self, tarfileobject):
        self.tarfileobject = tarfileobject

    def __iter__(self):
        return self

    def __next__(self):
        nextmember = self.tarfileobject.next()
        if nextmember:
            return nextmember
        else:
            raise StopIteration
