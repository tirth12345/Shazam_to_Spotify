import sounddevice as sd 
import scipy.io.wavfile as wav
import shazamio
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio

SPOTIPY_CLIENT_ID = '9fda4040c89142338477815b3af1215d'
SPOTIPY_CLIENT_SECRET = '8ca51e216eb54cb5a28ae94b6af6af1f'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback/'  # Default redirect URI
SCOPE = 'playlist-modify-public'



# Record audio function
def record_audio(filename=r'C:\Users\tirth\Desktop\Record\output.wav', duration=10, fs=44100): 
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until the recording is finished
    wav.write(filename, fs, recording)
    print("Recording saved to", filename)



# Recognize song using Shazam
async def recognize_song(filename=r'C:\Users\tirth\Desktop\Record\output.wav'):
    shazam = shazamio.Shazam()

    try:
        with open(filename, 'rb') as f:
            song_info = await shazam.recognize(f.read()) 
            print("Received response from Shazam:", song_info)
        
        if 'track' in song_info:
            return song_info['track']
        else:
            print("Track key not found in response.")
            return None
    except Exception as e:
        print("Error recognizing song:", e)
        return None


# if there is an existing playlist with the same name, songs will be added to it or else create a new playlist
def create_spotify_playlist(tracks):
    # Authenticate with Spotify
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE))

    user_id = sp.current_user()['id']
    playlists = sp.current_user_playlists()
    playlist_exists = False
    for playlist in playlists['items']:
        if playlist['name'] == 'Shazam Songs':
            playlist_exists = True
            playlist_id = playlist['id']
            break

    if not playlist_exists:
        playlist = sp.user_playlist_create(user_id, 'Shazam Songs', public=True)
        playlist_id = playlist['id']
    
    track_ids = []
    for track in tracks:
        result = sp.search(q=f"{track['title']} {track['subtitle']}", type='track')
        if result['tracks']['items']:
            track_ids.append(result['tracks']['items'][0]['id'])
    
    if track_ids:
        sp.user_playlist_add_tracks(user_id, playlist_id, track_ids)
        print(f"Playlist created: {playlist['external_urls']['spotify']}")
    else:
        print("No tracks found on Spotify.")

# Main function        
async def main():
    record_audio()
    
    song = await recognize_song()
    if song:
        print(f"Recognized Song: {song['title']} by {song['subtitle']}")
        
        create_spotify_playlist([song])
    else:
        print("Song not recognized or no track data available.")

# Run the main function

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass