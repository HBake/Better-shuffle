import spotipy, random, time, webbrowser
import spotipy.util as util
from datetime import datetime


username = 'OMITTED'
scope = 'playlist-modify-private playlist-modify-public user-library-read user-read-playback-state user-modify-playback-state user-read-currently-playing streaming app-remote-control'
playlist_id = 'OMITTED'  # likes randomized
#redirect_uri = 'http://localhost/'
redirect_uri = 'http://google.com/'


class Sandstorm:

    def __init__(self):
        self.auth = spotipy.oauth2.SpotifyOAuth(client_id='OMITTED',
                                                client_secret='OMITTED',
                                                redirect_uri=redirect_uri, scope=scope,
                                                cache_path='.cache-' + username, username=username)
        self.sp = spotipy.Spotify(auth=self.get_token())
        self.nextRandom = '2lylyZl9S7rbp2FUP5IS0r'

    def get_token(self):
        token_info = self.auth.get_cached_token()

        if token_info:
            access_token = token_info['access_token']
            return access_token
        else:
            webbrowser.open(self.auth.get_authorize_url())
            url = input('Paste response url here: ')
            code = self.auth.parse_response_code(url)
            access_token = self.auth.get_access_token(code)
            return access_token

    def refresh_token(self):
        cached_token = self.auth.get_cached_token()
        refresh_token = cached_token['refresh_token']
        new_token = self.auth.refresh_access_token(refresh_token)
        self.sp = spotipy.Spotify(auth=new_token['access_token'])
        return new_token

    def empty_playlist(self, playlist_id):
        self.sp.user_playlist_replace_tracks(username, playlist_id, [])

    def fill_playlist(self, playlist_id, tracks=None, track_ids=None, darude=True):
        if tracks:
            track_ids = [i['track']['id'] for i in tracks]

        if darude:
            track_ids = ['2lylyZl9S7rbp2FUP5IS0r'] + track_ids

        num_tracks = len(track_ids)
        for i in range(0, num_tracks, 100):
            self.sp.user_playlist_add_tracks(username, playlist_id, track_ids[i:min(num_tracks, 100 + i)])

    def pause(self):
        self.sp.pause_playback()

    def play(self, playlist_id, offset):

        playlist = self.sp.playlist(playlist_id)
        playlist_uri = playlist['uri']
        self.sp.start_playback(context_uri=playlist_uri, offset={'position': 1})

    def current_track(self):
        try:
            return self.sp.current_user_playing_track()
        except Exception as e:
            raise self.NoTrackPlayingException

    def set_shuffle(self, shuffle):
        self.sp.shuffle(shuffle)

    def get_liked_tracks(self):
        liked_tracks = []
        tracks = []
        limit = 50

        for i in range(10):
            tracks = self.sp.current_user_saved_tracks(limit=limit, offset=i*limit)['items']
            liked_tracks += tracks

            if len(tracks) < limit:
                break
        return liked_tracks

    def is_track_darude(self, track):
        return track['item']['uri'] == 'spotify:track:2lylyZl9S7rbp2FUP5IS0r'

    def run(self):
        fmt = "%Y-%m-d %H:%M:%S.%f"
        while True:
            try:
                current_track = self.current_track()

                if self.is_track_darude(current_track):
                    time_started = datetime.utcnow()
                    self.pause()
                    print("Darude sandstorm is playing")
                    self.set_shuffle(False)
                    print("Emptying playlist")
                    #self.empty_playlist(playlist_id)

                    if self.nextRandom:
        #                self.sp.user_playlist_add_tracks(username, playlist_id, ['2lylyZl9S7rbp2FUP5IS0r', self.nextRandom])
                        self.sp.user_playlist_replace_tracks(username, playlist_id, ['2lylyZl9S7rbp2FUP5IS0r', self.nextRandom])
                        time.sleep(1)
                        self.play(playlist_id, 1)
                        time_ended = datetime.utcnow()
                        print("playing song:", time_ended - time_started)
                        Random=self.nextRandom
                    #    input()

                    print("Collecting liked tracks")
                    liked_tracks = self.get_liked_tracks()
                    self.nextRandom = random.choice(liked_tracks)['track']['id']
                    print("Randomizing liked tracks")
                    random.shuffle(liked_tracks)

                    print("Filling playlist")
                    liked_tracks = [i for i in liked_tracks if i['track']['id'] != Random]
                    self.fill_playlist(playlist_id, tracks=liked_tracks, darude=False)

                    time_ended = datetime.utcnow()
                    print("playlist filled:", time_ended - time_started)

                else:
                    print("Darude sandstorm is not playing")

                pass

            except self.NoTrackPlayingException:
                print("refreshing token")
                self.refresh_token()

            except spotipy.client.SpotifyException:
                print("Spotify is paused")
                continue

            except Exception as e:
                print("Error: ", e.args, e.__context__)
                continue
            time.sleep(0.1)

    class NoTrackPlayingException(Exception):
        def __init__(self):
            pass


ss = Sandstorm()
ss.run()
