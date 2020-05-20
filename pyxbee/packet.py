import json
import logging

from abc import ABC
from hashlib import blake2b

from .const import PROTOCOL
from .exception import InvalidTypeException, InvalidFieldsException, InvalidInstanceException

log = logging.getLogger(__name__)


class _ABCPacket(ABC):

    _PACKETS = dict(PROTOCOL)

    # chiave per il digest
    _SECRET_KEY = None

    # tipi pacchetto per il protocollo standard
    class Type:
        DATA = '0'
        STATE = '1'
        NOTICE = '2'
        SETTING = '3'
        SIGNAL = '4'
        MESSAGE = '5'
        RASPBERRY = '6'
        VIDEO = '7'

    def __init__(self, content=None):
        if content is None:
            content = dict()
        self._content = self._decode(content)

    @property
    def content(self):
        return tuple(self._content.values())

    @property
    def content_dict(self):
        return self._content

    @property
    def protected_type(self):
        return (Packet.Type.SETTING,
                Packet.Type.SIGNAL,
                Packet.Type.MESSAGE,
                Packet.Type.RASPBERRY,
                Packet.Type.VIDEO)

    @property
    def secret_key(self):
        return self._SECRET_KEY

    @secret_key.setter
    def secret_key(self, key):
        if not isinstance(key, str):
            raise InvalidInstanceException

        self._SECRET_KEY = key

    @classmethod
    def protocol(cls, protocol=None):
        """Metodo per inserire un protocollo custom"""
        if isinstance(protocol, dict):
            cls._PACKETS = dict(protocol)
        elif isinstance(protocol, str):
            cls._PACKETS = dict(json.loads(protocol))
        else:
            cls._PACKETS = dict(PROTOCOL)

        return cls._PACKETS

    def _decode(self, data):
        """Se viene passato un dizionario aggiorna
        i valori da un pacchetto corrispondente vuoto;
        se viene passata una lista/tupla/stringa
        ne estrae i valori e li converte in dizionario.
        """
        self._check_data(data)

        if isinstance(data, dict):
            # ORDINE VALORI NON IMPORTANTE
            dic = dict(self._PACKETS[str(data['type'])])
            dic.update(data)
        else:
            # ORDINE VALORI IMPORTANTE
            dic = self._dictify(data)

        if dic['type'] in self.protected_type and self.secret_key:
            self._add_digest(dic)

        return dict(dic)

    def _check_data(self, data):
        if isinstance(data, dict):
            content = data.values()
            tipo = data['type']
        else:
            content = data if isinstance(data, (list, tuple)) else data.split(';')
            tipo = content[1]

        # check valid type
        if tipo not in self._PACKETS.keys():
            raise InvalidTypeException

        # check valid len
        if len(content) != len(self._PACKETS[tipo].values()):
            raise InvalidFieldsException

    def _dictify(self, data):
        if isinstance(data, str):
            data = [json.loads(item.lower()) if item.lower() in ('true', 'false')
                    else item for item in data.split(';')]

        content = list(data[::-1])
        res = dict(self._PACKETS[str(data[1])])
        for key, _ in res.items():
            res[key] = content.pop()

        return res

    def _add_digest(self, dic):
        h = blake2b(key=self.secret_key, digest_size=16)
        h.update(json.dumps(dic).encode('utf-8'))
        dic.update({'digest': h.hexdigest()})

    def __len__(self):
        return len(self._content)

    def __str__(self):
        return str(self._content)


class Packet(_ABCPacket):
    """
    Questa classe crea dei pacchetti
    contenitori sottoforma di dizionari o tuple
    e fornisce metodi per facilitare la
    comunicazione con il frontend e gli xbee
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def dest(self):
        return self.content[0] if len(self) > 0 else None

    @property
    def tipo(self):
        return self.content[1] if len(self) > 0 else None

    @property
    def value(self):
        return self.content[2:]

    @property
    def encode(self):
        return ';'.join(map(str, self.content))

    @property
    def jsonify(self):
        return json.dumps(self.content_dict)

    @property
    def dictify(self):
        return self.content_dict
