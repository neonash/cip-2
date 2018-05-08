# from rest_framework import serializers


class Error:
    def __init__(self):
        return

    def __init__(self, message, status):
        self.message = message
        self.status  = status
