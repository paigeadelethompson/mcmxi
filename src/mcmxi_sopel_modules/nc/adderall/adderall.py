import itertools as ITER
import json as JSON
import logging as L
import textwrap as TXT
import urllib.parse as URL
import types as TYPES
from ipaddress import IPv4Network as N4, IPv6Network as N6
import requests as WWW
from dns import resolver as DNS
import ast as AST
from pyroute2.iproute import IPRoute as IP
from sopel.logger import get_logger
from sopel import module
import socket as SOCK


# def setup(bot):
#     pass
#
#
# def configure(config):
#     pass


@module.commands('ipl')
@module.example('ip aa.bb.cc.dd')
def cmd_ip(bot, trigger) -> None:
    logger  = get_logger(__name__)
    IRC_TXT = irc_text_formatting()

    res = JSON.loads(WWW.get(
        "http://api.bgpview.io/ip/{ip_address}".format(
            ip_address = trigger.args[1].split(' ')[1] ) ).text)

    logger.info(res)

    [bot.say(
        "{prefix} {bold}{ptr_record}{reset} AS{as_number} {prefix_sample}".format(
            prefix        = IRC_TXT.meander,
            bold          = IRC_TXT.IRC_FMT_BOLD,
            reset         = IRC_TXT.IRC_FMT_RESET,
            ptr_record    = res.get("data"
            ).get("ptr_record"),
            as_number    = x.get("asn"
            ).get("asn"),
            prefix_sample = " ".join(set([x.get("prefix"
            ) for x in res.get("data"
            ).get("prefixes") ] ) ) )
    ) for x in res.get("data").get("prefixes")[ : 1 ]]


@module.commands('asn')
@module.example('asn 65534')
def cmd_asn(bot, trigger) -> None:
    get_logger(__name__)
    term_bin()
    IRC_TXT  = irc_text_formatting()

    res = JSON.loads(WWW.get(
        "https://api.bgpview.io/asn/{as_number}/prefixes".format(
            as_number = int(trigger.args[1].split(' ')[1].strip()))).text)

    # paste = TERM_BIN.term_bin(JSON.dumps(
    #     res,
    #     sort_keys = True,
    #     indent = True ) )
    #
    # logger.info(paste)
    paste = "https://api.bgpview.io/asn/{as_number}/prefixes".format(
            as_number = int(trigger.args[1].split(' ')[1].strip()))

    bot.say(
        " ".join([
            """
            {prefix}
            {_s_}{bold}      {name}         {reset}
            {_s_}            {description}
            {_s_}            {country}
            {_s_}            {cidr}
            {_s_}            {parent}
            {_s_}{italic}    continued:     {reset}
            {_s_}{underline} {paste_link}   {reset}
            """.replace(
                " ",
                ""
            ).format(
                _s_         = " ",
                prefix      = IRC_TXT.meander,
                bold        = IRC_TXT.IRC_FMT_BOLD,
                italic      = IRC_TXT.IRC_FMT_ITALIC,
                underline   = IRC_TXT.IRC_FMT_UNDERLINE,
                reset       = IRC_TXT.IRC_FMT_RESET,
                name        = x.get("name"),
                description = x.get("description"),
                country     = x.get("country_code"),
                cidr        = x.get("prefix"),
                parent      = x.get("parent"
                ).get("rir_name"),
                paste_link  = paste ) for x in list(res.get("data"
                ).get("ipv4_prefixes"
                ) + res.get("data"
                ).get("ipv6_prefixes")
                )[ :1 ] ] ).replace(
            "\r\n",
            ""
        ).replace(
            "\n",
            "") )


@module.commands('proxy')
@module.example('proxy')
def cmd_proxy(bot, trigger) -> None:
    logger  = get_logger(__name__)
    IRC_TXT = irc_text_formatting()

    res = JSON.loads(WWW.get(
        "http://pubproxy.com/api/proxy").text)

    logger.info(res)

    bot.say(
        "{prefix} {underline}{bold}{protocol_handler}{reset}{underline}://{url}:{port}".format(
            prefix           = IRC_TXT.meander,
            underline        = IRC_TXT.IRC_FMT_UNDERLINE,
            bold             = IRC_TXT.IRC_FMT_BOLD,
            reset            = IRC_TXT.IRC_FMT_RESET,
            protocol_handler =  res.get(
                "data"
            )[ 0 ].get(
                "type"
            ),
            url              = res.get(
                "data"
            )[ 0 ].get(
                "ip"
            ),
            port             = res.get(
                "data"
            )[ 0 ].get("port") ) )


@module.commands('seerx')
@module.example('seerx search query')
def cmd_searx(bot, trigger) -> None:
    logger  = get_logger(__name__)
    IRC_TXT = irc_text_formatting()

    req = WWW.get(
        "https://searx.everdot.org/?q={}&format=json".format(
            " ".join(trigger.args[1].split(' ')[1: ] ).strip(' ')))

    res = JSON.loads(req.text)

    logger.info(res)

    bot.say(
        """
        {prefix}
        {_s_}{bold}          {results}                      {reset} {_s_} results
        {_s_}{bold}          {answers}                      {reset} {_s_} answers
        {_s_}{bold}          {corrections}                  {reset} {_s_} corrections
        {_s_}{bold}          {info_boxes}                   {reset} {_s_} info {_s_} boxes
        {_s_}{bold}          {suggestions}                  {reset} {_s_} suggestions
        {_s_}{bold}          {unresponsive_engines}         {reset} {_s_} unresponsive {_s_} engines
        {_s_}                                                             were {_s_} found {_s_} for {_s_} query
        {_s_}{italic}        {question}                     {reset}
        {_s_}{underline}     {url}                          {reset}
        """.replace(
            "\n",
            " "
        ).replace(
            " ",
            ""
        ).strip(
            " "
        ).format(
            _s_                  = " ",
            prefix               = IRC_TXT.meander,
            bold                 = IRC_TXT.IRC_FMT_BOLD,
            italic               = IRC_TXT.IRC_FMT_ITALIC,
            reset                = IRC_TXT.IRC_FMT_RESET,
            underline            = IRC_TXT.IRC_FMT_UNDERLINE,
            results              = len(res.get(
                "results")) or 0,
            answers              = len(res.get(
                "answers")) or 0,
            corrections          = len(res.get(
                "corrections")) or 0,
            info_boxes           = len(res.get(
                "infoboxes")) or 0,
            suggestions          = len(res.get(
                "suggestions")) or 0,
            unresponsive_engines = len(res.get(
                "unresponsive_engines")) or 0,
            question             = res.get(
                "query"),
            url                  = req.url.replace("&format=json", "")))


@module.commands('cidr')
@module.example('cidr 100.64.0.0/10')
def cmd_cidr(bot, trigger) -> None:
    get_logger(__name__)
    IRC_TXT = irc_text_formatting()

    [ bot.say(x) for x in map(lambda c: '''
    {prefix}
    {_s_}                                    {_s_} {bold} size:        {reset}
    {_s_}{underline} {num_addresses} {reset} {_s_} {bold} start:       {reset}
    {_s_}{underline} {start}         {reset} {_s_} {bold} end:         {reset}
    {_s_}{underline} {end}           {reset} {_s_} {bold} netmask:     {reset}
    {_s_}{underline} {netmask}       {reset} {_s_} {bold} global:      {reset}
    {_s_}{underline} {_global}       {reset} {_s_} {bold} private:     {reset}
    {_s_}{underline} {private}       {reset} {_s_} {bold} link-local:  {reset}
    {_s_}{underline} {link_local}    {reset} {_s_} {bold} multicast:   {reset}
    {_s_}{underline} {multicast}     {reset} {_s_} {bold} unspecified: {reset}
    {_s_}{underline} {unspecified}   {reset} {_s_} {bold} supernet:    {reset}
    {_s_}{underline} {supernet}      {reset}
    '''.replace(
        "\n",
        ""
    ).replace(
        " ",
        ""
    ).strip(
        " "
    ).format(
        _s_           = " ",
        bold          = IRC_TXT.IRC_FMT_BOLD,
        underline     = IRC_TXT.IRC_FMT_UNDERLINE,
        reset         = IRC_TXT.IRC_FMT_RESET,
        prefix        = IRC_TXT.meander,
        num_addresses = c.num_addresses,
        start         = c.network_address.exploded,
        end           = c.broadcast_address,
        netmask       = c.with_netmask,
        _global       = c.is_global,
        private       = c.is_private,
        link_local    = c.is_link_local,
        multicast     = c.is_multicast,
        unspecified   = c.is_unspecified,
        supernet      = c.supernet()
    ), [ x.find(":") != -1
         and N6(x)
         or N4(x)
         for x in trigger.args[1].split(' ')[1: ] ] ) ]


@module.commands('dns')
@module.example('dns A google.com')
def cmd_dns(bot, trigger) -> None:
    get_logger(__name__)
    IRC_TXT = irc_text_formatting()
    args    = trigger.args[1].split(' ')[1: ]
    rdtype  = (len(args) > 1) and args[ 0 ] or "A"
    Q       = (len(args) > 1) and args[ 1 ] or args[ 0 ]

    answer = DNS.Resolver().resolve(
        rdtype = rdtype,
        qname  = Q)

    bot.say(
        "{prefix} {bold}{c_name}{reset} @{name_server} rrset: {rr_set} ".format(
            prefix      = IRC_TXT.meander,
            bold        = IRC_TXT.IRC_FMT_BOLD,
            reset       = IRC_TXT.IRC_FMT_RESET,
            c_name      = answer.canonical_name,
            name_server = answer.nameserver,
            rr_set      = answer.rrset.to_text() ) )


class irc_text_formatting:
    """
    """
    def __init__(self):
        self.RED_2 = None
        self.BLUE = None
        self.IRC_FMT_COLOR     = None
        self.IRC_FMT_UNDERLINE = None
        self.IRC_FMT_ITALIC    = None
        self.IRC_FMT_RESET     = None
        self.IRC_FMT_BOLD      = None
        self.l                 = L.getLogger(__name__)

        '''
        '''
        self.default_bg_color  = ITER.cycle([ 99 ])

        '''
        '''
        self.art               = lambda a: [ (x, chr(y)
        ) for x, y in zip(range(len(range(0x2500, 0x25FF) )
        ), range(0x2500, 0x25FF)
        ) if x == a ][ 0 ][ 1 ]

        '''
        '''
        self.art_reverse       = lambda z: [ y for x, y in zip(range(
            0x2500,
            0x25FE
        ), range(len(range(
            0x2500,
            0x25FE) ) ) ) if ord(self.art(y) ) == z or self.art(y) == z ]

        '''
        Generic error message
        '''
        self.fallback          = "".join([ chr(x) for x in [
            0x00AF,
            0x005C,
            0x005F,
            0x0028,
            0x30C4,
            0x0029,
            0x005F,
            0x002F,
            0x00AF ] ] )

        '''
        Default color map for IRC color interpolation
        '''
        self.default_color_map = (
            lambda bg = None: ITER.cycle(ITER.chain.from_iterable([list(map(lambda x: x != 88 and (
                x,
                (bg != None)
                and next(bg)
                or next(self.default_color_map)
            ) or (x - 12, 88), x) ) for x in map(lambda z: [index for index in list(list(ITER.accumulate(range(
                z,
                z + 7
            ), lambda x, y: x == 0 and z or x + 12) ),
            )  ], range(16, 28) ) ] ) ) )

        '''
        IRC text formatting class property names (bound later)
        '''
        self.format_chars      = [
            "IRC_FMT_BOLD",
            "IRC_FMT_COLOR",
            "IRC_FMT_ITALIC",
            "IRC_FMT_REVERSE_COLOR",
            "IRC_FMT_UNDERLINE",
            "IRC_FMT_STRIKETHROUGH",
            "IRC_FMT_MONOSPACE",
            "IRC_FMT_RESET" ]

        '''
        color palette table names, used to store interpolated color palettes as individual lists in class
        properties (initialized in constructor)
        '''
        self.palletes          = [
            "RED",
            "ORANGE",
            "YELLOW",
            "GREEN",
            "GREEN_2",
            "GREEN_3",
            "AQUA",
            "BLUE",
            "BLUE_2",
            "PURPLE",
            "PURPLE_2",
            "RED_2" ]

        # Color PRIVMSG
        self.color_say         = (
            lambda bot, message, target, pallete = ITER.cycle( [ (0, 1) ]
            ): [bot.connection.privmsg(target, "".join(["{}{},{}{}{}".format(
                self.IRC_FMT_COLOR,
                x[ 1 ][ 0 ],
                x[ 1 ][ 1 ],
                x[ 0 ],
                self.IRC_FMT_RESET
            ) for x in zip(list(index
            ), pallete ) ] ) ) for index in TXT.wrap(message, 53) ] )

        # Random light shades from random color palettes
        self.random_light      = lambda: ITER.cycle(R.sample([self.__getattribute__(x
        )[ 4 ] for x in self.palletes ], len(self.palletes) ) )

        # Default message prefix art
        self.meander           = "{}{}{}".format(
            self.art(155),
            self.art(156),
            self.art(159) )

        self.meandros         = [[
            self.art(84),
            self.art(80),
            self.art(80),
            self.art(80),
            self.art(80),
            self.art(87),
            " ",
            self.art(81)
        ],[ self.art(81),
            " ",
            self.art(84),
            self.art(80),
            self.art(80),
            self.art(93),
            " ",
            self.art(81)
        ],[ self.art(81),
            " ",
            self.art(90),
            self.art(80),
            self.art(80),
            self.art(80),
            self.art(80),
            self.art(93) ] ]

        self.trans_flag       = lambda: ["".join(map(lambda l: "{color}{fg},{bg}{back_fill}{reset}".format(
            color     = self.IRC_FMT_COLOR,
            fg        = x[ 1 ][ 0 ],
            bg        = x[ 1 ][ 0 ],
            back_fill = l,
            reset     = self.IRC_FMT_RESET ), x[ 0 ])
        ) for x in zip( [ [ self.art(136) ] * 30 ] * 5, (
            self.BLUE[  5 ],
            self.RED_2[ 4 ],
            self.RED_2[ 6 ],
            self.RED_2[ 4 ],
            self.BLUE[  5 ] ) ) ]

        [ self.__setattr__(y, "{}".format(x) ) for x, y in zip( [
            chr(0x02),
            chr(0x03),
            chr(0x1D),
            chr(0x16),
            chr(0x1F),
            chr(0x1E),
            chr(0x11),
            chr(0x0F)
        ], self.format_chars ) ]

        # Create color palette class properties from color palette names
        [ (not self.__dict__.get(x[ 1 ][ 0 ]
        ) and (self.__setattr__(x[ 1 ][ 0 ], list()
        ) is None and self.__getattribute__(x[ 1 ][ 0 ])
        ) or self.__getattribute__(x[ 1 ][ 0 ] )
        ).append((x[ 1 ][ 1 ], x[ 1 ][ 2 ] )
        ) for x in zip(range(7 * 12
        ), ITER.cycle(ITER.chain.from_iterable([list(map(lambda x: x[ 1 ] != 88 and (x[ 0 ], x[ 1 ], next(self.default_bg_color)
        ) or (x[ 0 ], x[ 1 ] - 12, next(self.default_bg_color) ), x ) ) for x in map(lambda z: [(z[ 1 ], index
        ) for index in list(ITER.accumulate(range(z[ 0 ], z[ 0 ] + 7
        ), lambda x, y: x == 0 and z[ 0 ] or x + 12 )
        ) ], zip(range(16, 28), self.palletes ) ) ] ) ) ) ]


class term_bin:
    """
    """
    def __init__(self):
        self.l         = L.getLogger(__name__)

    '''
    Posts data to TermBin and returns a URL to the term-paste
    '''
    def term_bin(self, data) -> "":
        self.l.debug(data)

        sock           = SOCK.socket(
            SOCK.AF_INET,
            SOCK.SOCK_STREAM)

        server_address = (
            'termbin.com',
            9999)

        sock.connect(server_address)

        sock.sendall(bytes(
            "{}".format(data),
            "UTF-8") )

        sock.sendall(bytes(
            "\0",
            "UTF-8") )

        return(sock.recv(
            4096
        ).decode(
        ).replace(
            '\r\n',
            '\n') )


class utilities:
    DNS                        = DNS.Resolver()

    '''
    Determine whether type of f is one of the many function or method types
    '''
    is_func_or_meth            = lambda f: (
        TYPES.FunctionType
        == type(f)
        or TYPES.BuiltinFunctionType
        == type(f)
        or TYPES.BuiltinMethodType
        == type(f)
        or TYPES.MethodType
        == type(f)
        or TYPES.LambdaType
        == type(f)
    ) and True or False

    '''
    '''
    def __init__(self):
        self.l                 = L.getLogger(__name__)


    '''
    grabs an arbitrary HTTP/s response 
    '''
    def grab(self, url, depth = 0) -> "":
        logger.info(url)

        req = WWW.get(
            url,
            stream          = True,
            allow_redirects = False)

        logger.info(req)

        if req.is_redirect:
            if self.verify_address(req.headers.get("Location"
            ) or req.headers.get("location")
            ) and depth <= 4:

                return(self.grab(req.headers.get("Location"
                ) or req.headers.get("location"), depth + 1) )

            else:
                raise Exception("no redirect location specified or too many redirects")

        ret = []

        try:
            [ ret.append(index) for index in req.iter_content(
                chunk_size     = 8192,
                decode_unicode = True)
              if ( len(bytes("".join(ret), "UTF-8") ) < 500000 * 4 )
              or ( _ for _ in () ).throw(StopIteration) ]

        except StopIteration:
            self.l.debug("max size read")

        return "".join(ret)

    '''
    Verify that the destination URL doesn't resolve to something
    unreasonable, and that it doesn't resolve to any addresses
    assigned to the server running the bot
    '''
    def verify_address(self, url) -> bool:
        addr = None

        try:
            addr = N6("{}/128".format(self.DNS.resolve(URL.urlparse(url
            ).netloc, rdtype = "AAAA"
            ).response.answer.pop(
            ).to_text(
            ).split(
            ).pop()))

        except:
            try:
                addr = N4("{}/32".format(self.DNS.resolve(URL.urlparse(url
                ).netloc, rdtype = "A"
                ).response.answer.pop(
                ).to_text(
                ).split(
                ).pop()))

            except Exception as ex:
                self.l.exception(ex)

        finally:
            return(addr is not None
                   and addr.is_global
                   and not addr.is_reserved
                   and not addr.is_multicast
                   and not addr.is_link_local
                   and not addr.is_private
                   and not addr.is_unspecified
                   and len([x.get("attrs"
                   )[ 0 ][ 1 ] for x in IP(
                   ).get_addr() if x.get("attrs")[ 0 ][ 1 ] == addr.network_address]) == 0)

    '''
    Guesses the value type of a parameter (parameterization of calls to method calls from IRC via commands)
    '''
    def guess_type(self, s) -> type:
        try:
            value = AST.literal_eval(s)

        except ValueError or SyntaxError:
            self.l.debug("computed type {}".format(str) )
            return str

        else:
            self.l.debug("computed type {}".format(type(value) ) )
            return type(value)
