# Copyright (C) 2006-2010  Johannes Sasongko <sasongko@gmail.com>
# Copyright (C) 2010  Mathias Brodala <info@noctus.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import urllib2

from xl import (
    covers,
    providers
)

import musicbrainzngs

logger = logging.getLogger(__name__)

musicbrainzngs.set_useragent(
    'Exaile MusicBrainz Covers',
    '1.0.0',
    'http://exaile.org/'
)

def enable(exaile):
    """
        Enables the plugin
    """
    providers.register('covers', MusicBrainzCoverSearch())

def disable(exaile):
    """
        Disables the plugin
    """
    providers.unregister('covers', providers.get_provider('covers', 'musicbrainz'))

class MusicBrainzCoverSearch(covers.CoverSearchMethod):
    """
        Searches MusicBrainz for an album cover
    """
    name = 'musicbrainz'
    title = 'MusicBrainz'
    __caa_url ='http://coverartarchive.org/release/{mbid}/front-{size}' 

    def find_covers(self, track, limit=-1):
        """
            Performs the search
        """
        try:
            artist = track.get_tag_raw('artist')[0]
            album = track.get_tag_raw('album')[0]
        except (AttributeError, TypeError):
            return []

        result = musicbrainzngs.search_releases(
            release=album,
            artistname=artist,
            format='CD',
            limit=3 # Unlimited search is slow
        )

        if result['release-list']:
            mbids = [a['id'] for a in result['release-list']]
            
            # Check the actual availability of the covers
            for mbid in mbids[:]:
                try:
                    url = self.__caa_url.format(mbid=mbid, size=250)
                    response = urllib2.urlopen(url)
                except urllib2.HTTPError:
                    mbids.remove(mbid)

            # For now, limit to small sizes
            mbids = [mbid + ':250' for mbid in mbids]

            return mbids

        return []

    def get_cover_data(self, db_string):
        """
            Get the image data
        """
        data = None
        mbid, size = db_string.split(':')
        url = self.__caa_url.format(mbid=mbid, size=size)

        try:
            logger.debug('Fetching cover from {url}'.format(url=url))
            response = urllib2.urlopen(url)
        except urllib2.HTTPError:
            pass
        else:
            data = response.read()
            response.close()

        return data