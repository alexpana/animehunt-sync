import urllib2
from gzip import GzipFile
from StringIO import StringIO
import xml.etree.ElementTree
import MySQLdb
from sets import ImmutableSet

ANIDB_SOURCE = "http://anidb.net/api/animetitles.xml.gz"

DB_CONNECTION = {
    "user": "root",
    "passwd": "oscarwilde",
    "db": "animehunt"}

CACHE = {}

def log_event(event):
    CACHE["last_event"] = event
    print event,


def log_result(result):
    print "." * (60 - (len(CACHE["last_event"]) + len(result) + 2)) + " " + result


def read_remote():
    log_event("Fetching list of titles from anidb.net")
    reply = urllib2.urlopen(ANIDB_SOURCE)
    log_result("Done")

    log_event("Decompressing")
    decompressed = GzipFile(fileobj=StringIO(reply.read()))
    log_result("Done")
    return decompressed


def read_local(filename):
    log_event("Reading local file")

    log_event("Decompressing")
    decompressed = GzipFile(fileobj=StringIO())
    log_result("Done")
    return decompressed


titlesGzipFile = read_remote()

log_event("Searching for titles")
rootXmlElement = xml.etree.ElementTree.fromstring(titlesGzipFile.read())

all_titles = {}

for element in rootXmlElement:
    element_titles = {}
    for title in element:
        if title.get('type') == 'official' and title.get('{http://www.w3.org/XML/1998/namespace}lang') == 'en':
            element_titles["official-en"] = title.text
        if title.get('type') == 'syn' and title.get('{http://www.w3.org/XML/1998/namespace}lang') == 'en':
            element_titles["syn-en"] = title.text
        if title.get('type') == 'main':
            element_titles["main"] = title.text

    entry = ["", ""]
    if 'official-en' in element_titles.keys():
        entry[0] = element_titles['official-en']
    elif 'syn-en' in element_titles.keys():
        entry[0] = element_titles['syn-en']
    else:
        entry[0] = element_titles['main']

    entry[1] = element_titles['main']

    all_titles[entry[0]] = entry[1]

titles = all_titles.keys()

log_result("Found %d / %d" % (len(titles), len(rootXmlElement)))

log_event("Connecting to the database")
connection = MySQLdb.connect(**DB_CONNECTION)
log_result("Success")

log_event("Retrieving anime titles from database")
cursor = connection.cursor()
cursor.execute("SELECT title from anime")
dbTitles = cursor.fetchall()
log_result("Found %d" % len(dbTitles))

remoteSet = ImmutableSet(titles)
localSet = ImmutableSet(map(lambda x: x[0], dbTitles))

log_event("Searching new titles")
updateSet = remoteSet.difference(localSet)
newTitlesCount = len(updateSet)
log_result("Found %d" % newTitlesCount)

log_event("Adding new titles")
cursor.executemany(
    "INSERT INTO anime (title, title_jp, type, status, summary, episode_count) VALUES (%s, %s, %s, %s, %s, %s)",
    map(lambda x: (x, all_titles[x], "-1", "-1", "", "-1"), updateSet)
)

log_result("Added %d" % newTitlesCount)

connection.commit()