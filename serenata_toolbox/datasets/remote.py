import configparser
from functools import partial
import os

import boto3

from serenata_toolbox.datasets.contextmanager import status_message


class RemoteDatasets:

    # Issue here! (../)
    CONFIG = '../config.ini'

    def __init__(self):
        self.credentials = None

        if not self.config_exists:
            print('Could not find {} file.'.format(self.CONFIG))
            print('You need Amzon section in it to interact with S3')
            print('(Check config.ini.example if you need a reference.)')
            return

        settings = configparser.RawConfigParser()
        settings.read(self.CONFIG)
        self.settings = partial(settings.get, 'Amazon')

        try:
            self.credentials = {
                'aws_access_key_id': self.settings('AccessKey'),
                'aws_secret_access_key': self.settings('SecretKey'),
                'region_name': self.settings('Region')
            }
        except configparser.NoSectionError:
            msg = (
                'You need an Amazon section in {} to interact with S3 '
                '(Check config.ini.example if you need a reference.)'
            )
            print(msg.format(self.CONFIG))

    @property
    def config_exists(self):
        return all((os.path.exists(self.CONFIG), os.path.isfile(self.CONFIG)))

    @property
    def bucket(self):
        if hasattr(self, 'settings'):
            try:
                return self.settings('Bucket')
            except configparser.NoSectionError:
                return None

    @property
    def s3(self):
        if hasattr(self, 'client'):
            return self.client

        if self.credentials:
            self.client = boto3.client('s3', **self.credentials)
            return self.s3

        return None

    @property
    def all(self):
        if self.s3 and self.bucket:
            response =  self.s3.list_objects(Bucket=self.bucket)
            yield from (obj.get('Key') for obj in response.get('Contents', []))

    def upload(self, file_path):
        if self.s3 and self.bucket:
            _, file_name = os.path.split(file_path)
            with status_message('Uploading {}…'.format(file_name)):
                self.s3.upload_file(file_path, self.bucket, file_name)

    def delete(self, file_name):
        if self.s3 and self.bucket:
            with status_message('Deleting {}…'.format(file_name)):
                self.s3.delete_object(Bucket=self.bucket, Key=file_name)
