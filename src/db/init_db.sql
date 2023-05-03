CREATE TABLE IF NOT EXISTS Games (
    first_player INT,
    second_player INT,
    game_state INT NOT NULL
);

CREATE TABLE IF NOT EXISTS WaitingPlayers (
    chat_id INT NOT NULL UNIQUE
);
