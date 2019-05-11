from .base import Const, Packet, Transmitter

# avvio trasmissione xbee
transmiter = Transmitter()

# Constanti per il dizionario
CONST = Const()

# questa classe istazia l'antenna
# della bici corrispondente e conserva
# i dati trasmetti sottoforma di Packet,
# si occupa anche dell'invio di
# pacchetti verso l'antenna server
#
# id --> codice con cui viene identif. nei pacchetti
# address --> indirizzo dell'antenna


class Taurus:
    def __init__(self, id, address):
        self.address = address
        self.id = id

        # inserisce l'istanza corrente
        # nei listener dell'antenna
        # del server
        transmiter.listener = self

        # memorizza i dati sottoforma
        # di pacchetti ricevuti dalla bici
        self.__memoize = dict()

    @property
    def data(self):
        data = self.__memoize.get(COSNT.DATA).jsonify
        return data if data != None else {}

    @property
    def settings(self):
        settings = self.__memoize.get(CONST.SETTING).jsonify
        return settings if settings != None else {}

    # TODO: Inserire gli altri pacchetti

    # DIREZIONE: server --> bici
    def send(self, packet):
        transmiter.send(self.address, Packet(packet))

    def receive(self, packet):
        type = packet.content[1]
        self.__memoize.update({type: packet})

    def __str__(self):
        return self.id + ' -- ' + self.address
