# -*- coding: utf-8 -*-
##
## This file is part of Indico.
## Copyright (C) 2002 - 2012 European Organization for Nuclear Research (CERN).
##
## Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico;if not, see <http://www.gnu.org/licenses/>.

from contextlib import contextmanager
from MaKaC.common.logger import Logger
from MaKaC.plugins.Collaboration.Vidyo.api.client import AdminClient, UserClient
from suds import WebFault
from MaKaC.plugins.Collaboration.Vidyo.common import VidyoConnectionException
from urllib2 import URLError


AUTOMUTE_API_PROFILE = "NoAudioAndVideo"


class ApiBase(object):
    """ Provides the _handleServiceCallException method
    """

    @classmethod
    def _handleServiceCallException(cls, e):
        Logger.get("Vidyo").exception("Service call exception")
        cause = e.args[0]
        if type(cause) is tuple and cause[0] == 401:
            raise VidyoConnectionException(e)
        elif type(e) == URLError:
            raise VidyoConnectionException(e)
        else:
            raise


class AdminApi(ApiBase):
    """ This class performs low-level operations by getting the corresponding
        client and calling a SOAP service.
        We write info statements to the log with the details of what we are doing.
        Each class method performs a single service call to Vidyo.
    """

    @classmethod
    def _api_operation(cls, service, *params, **kwargs):
        try:
            vidyoClient = AdminClient.getInstance()
        except Exception, e:
            raise VidyoConnectionException(e)
        try:
            return getattr(vidyoClient.service, service)(*params, **kwargs)
        except WebFault, e:
            raise
        except Exception, e:
            cls._handleServiceCallException(e)

    @classmethod
    def addRoom(cls, newRoom, confId, bookingId):
        return cls._api_operation('addRoom', newRoom)

    @classmethod
    def updateRoom(cls, roomId, updatedRoom, confId, bookingId):
        return cls._api_operation('updateRoom', roomId, updatedRoom)

    @classmethod
    def getRooms(cls, searchFilter, confId, bookingId):
        return cls._api_operation('getRooms', searchFilter)

    @classmethod
    def getRoom(cls, roomId, confId, bookingId):
        return cls._api_operation('getRoom', roomId)

    @classmethod
    def deleteRoom(cls, roomId, confId, bookingId):
        return cls._api_operation('deleteRoom', roomId)

    @classmethod
    def setAutomute(cls, roomId, enabled, confId, bookingId):
        if enabled:
            return cls._api_operation('setRoomProfile', roomId, AUTOMUTE_API_PROFILE)
        else:
            return cls._api_operation('removeRoomProfile', roomId)

    @classmethod
    def getAutomute(cls, roomId, confId, bookingId):
        return cls._api_operation('getRoomProfile', roomId)

    @classmethod
    def connectRoom(cls, roomId, confId, bookingId, legacyMember):
        return cls._api_operation('inviteToConference', roomId, entityID=legacyMember)


class UserApi(ApiBase):
    """ This class performs low-level operations by getting the corresponding
        client and calling a SOAP service.
        We write info statements to the log with the details of what we are doing.
    """


    @classmethod
    def search(cls, searchFilter, confId, bookingId):
        #Logger.get('Vidyo').info("""Evt:%s, booking:%s, opening connection to Vidyo Admin API""" % (confId, bookingId))
        try:
            vidyoClient = UserClient.getInstance()
        except Exception, e:
            raise VidyoConnectionException(e)

        #Logger.get('Vidyo').info("""Evt:%s, booking:%s, calling User API's search operation with filter: %s""" %
        #                                 (confId, bookingId, str(searchFilter)))
        try:
            answer = vidyoClient.service.search(searchFilter)
        #    Logger.get('Vidyo').info("""Evt:%s, booking:%s, User API's search operation got answer: %s""" %
        #                                     (confId, bookingId, str(answer)))

            return answer

        except WebFault, e:
            Logger.get('Vidyo').exception("""Evt:%s, booking:%s, User API's search operation operation got WebFault: %s""" %
                                    (confId, bookingId, e.fault.faultstring))
            raise

        except Exception, e:
            cls._handleServiceCallException(e)
