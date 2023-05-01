CREATE TABLE IF NOT EXISTS Games (
    first_player INT NOT NULL,
    second_player INT NOT NULL,
    game_state INT NOT NULL
);

CREATE TABLE IF NOT EXISTS WaitingPlayers (
    chat_id INT NOT NULL,
    player_name TEXT NOT NULL
);
