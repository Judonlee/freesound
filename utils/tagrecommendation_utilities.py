#
# Freesound is (c) MUSIC TECHNOLOGY GROUP, UNIVERSITAT POMPEU FABRA
#
# Freesound is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Freesound is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     See AUTHORS file.
#

import settings, traceback, logging
#from django.core.cache import cache
from tagrecommendation.client import TagRecommendation

logger = logging.getLogger('web')

def get_recommended_tags(input_tags, max_number_of_tags = 10 ):

    if preset not in PRESETS:
        preset = DEFAULT_PRESET

    cache_key = "similar-for-sound-%s-%s" % (sound.id, preset)

    # Don't use the cache when we're debugging
    if settings.DEBUG:
        similar_sounds = False
    else:
        similar_sounds = cache.get(cache_key)

    if not similar_sounds:
        try:
            similar_sounds = [ [int(x[0]),float(x[1])] for x in Similarity.search(sound.id, preset = preset, num_results = SIMILAR_SOUNDS_TO_CACHE)]
        except Exception, e:
            logger.debug('Could not get a response from the similarity service (%s)\n\t%s' % \
                         (e, traceback.format_exc()))
            similar_sounds = []

        if len(similar_sounds) > 0:
            cache.set(cache_key, similar_sounds, SIMILARITY_CACHE_TIME)

    return similar_sounds[0:num_results]

