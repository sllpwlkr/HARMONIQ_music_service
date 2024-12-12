-- Users & Admins
CREATE TABLE roles (
    role_id serial PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE users (
    user_id serial PRIMARY KEY,
    login VARCHAR(255) NOT NULL,
    hash_password VARCHAR(255) NOT NULL,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE actions (
    action_id serial PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE log_actions (
    log_id serial PRIMARY KEY,
    user_id INT,
    action_id INT,
    action_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (action_id) REFERENCES actions(action_id)
);

-- Artists
CREATE TABLE artists (
    artist_id serial PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Genres
CREATE TABLE genres (
    genre_id serial PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);



-- Songs
CREATE TABLE songs (
    song_id serial PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    artist_id INT NOT NULL,
    duration TIME NOT NULL,
    genre_id INT,
    CONSTRAINT unique_song_artist_album UNIQUE (name, artist_id),
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE SET NULL
);

-- Playlists
CREATE TABLE playlists (
    playlist_id serial PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date_creation DATE NOT NULL
);

-- User-Playlist Relationship
CREATE TABLE users_playlists (
    user_id INT NOT NULL,
    playlist_id INT NOT NULL,
    PRIMARY KEY (user_id, playlist_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE
);

-- Playlist-Songs Relationship
CREATE TABLE playlists_songs (
    playlist_id INT NOT NULL,
    song_id INT NOT NULL,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
);

-- Counts of listen
CREATE TABLE songs_listens (
    listen_id serial PRIMARY KEY,
    song_id INT NOT NULL,
    count_listen int default 0 ,
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION log_add_song()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 1, NOW());  -- action_id = 1 для 'Add song'
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_add_song
AFTER INSERT ON songs
FOR EACH ROW
EXECUTE FUNCTION log_add_song();

CREATE OR REPLACE FUNCTION log_delete_song()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 2, NOW());  -- action_id = 2 для 'Delete song'
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_delete_song
AFTER DELETE ON songs
FOR EACH ROW
EXECUTE FUNCTION log_delete_song();

CREATE OR REPLACE FUNCTION log_add_artist()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 3, NOW());  -- action_id = 3 для 'Add artist'
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_add_artist
AFTER INSERT ON artists
FOR EACH ROW
EXECUTE FUNCTION log_add_artist();

CREATE OR REPLACE FUNCTION log_delete_artist()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 4, NOW());  -- action_id = 4 для 'Delete artist'
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_delete_artist
AFTER DELETE ON artists
FOR EACH ROW
EXECUTE FUNCTION log_delete_artist();

CREATE OR REPLACE FUNCTION log_add_genre()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 5, NOW());  -- action_id = 5 для 'Add genre'
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_add_genre
AFTER INSERT ON genres
FOR EACH ROW
EXECUTE FUNCTION log_add_genre();

CREATE OR REPLACE FUNCTION log_delete_genre()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 6, NOW());  -- action_id = 6 для 'Delete genre'
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_delete_genre
AFTER DELETE ON genres
FOR EACH ROW
EXECUTE FUNCTION log_delete_genre();

CREATE OR REPLACE FUNCTION log_registration()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (NEW.user_id, 7, NOW());  -- action_id = 7 для 'Registration'
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_registration
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION log_registration();

CREATE OR REPLACE FUNCTION log_add_playlist()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 8, NOW());  -- action_id = 8 для 'Add playlist'
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_add_playlist
AFTER INSERT ON playlists
FOR EACH ROW
EXECUTE FUNCTION log_add_playlist();

CREATE OR REPLACE FUNCTION log_delete_playlist()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 9, NOW());  -- action_id = 9 для 'Delete playlist'
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_delete_playlist
AFTER DELETE ON playlists
FOR EACH ROW
EXECUTE FUNCTION log_delete_playlist();

CREATE OR REPLACE FUNCTION log_add_song_in_playlist()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 10, NOW());  -- action_id = 10 для 'Add song in playlist'
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_add_song_in_playlist
AFTER INSERT ON playlists_songs
FOR EACH ROW
EXECUTE FUNCTION log_add_song_in_playlist();

CREATE OR REPLACE FUNCTION log_delete_song_from_playlist()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO log_actions (user_id, action_id, action_time)
  VALUES (current_setting('session.user_id')::INT, 11, NOW());  -- action_id = 11 для 'Delete song from playlist'
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_delete_song_from_playlist
AFTER DELETE ON playlists_songs
FOR EACH ROW
EXECUTE FUNCTION log_delete_song_from_playlist();
