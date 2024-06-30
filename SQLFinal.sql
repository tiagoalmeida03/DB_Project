CREATE TABLE login (
	id	 BIGSERIAL,
	email	 VARCHAR(512) NOT NULL UNIQUE,
	password VARCHAR(512) NOT NULL,
	username VARCHAR(512) NOT NULL UNIQUE,
	PRIMARY KEY(id)
);

CREATE TABLE pessoa (
	nome		 VARCHAR(512) NOT NULL,
	morada		 VARCHAR(512) NOT NULL,
	datacriacao	 TIMESTAMP NOT NULL,
	telefone	 VARCHAR(512) NOT NULL,
	login_id	 BIGINT,
	codigopostal BIGINT NOT NULL,
	nomerua	 VARCHAR(512) NOT NULL,
	pais	 VARCHAR(512) NOT NULL,
	cidade	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(login_id),
	CONSTRAINT pessoa_fk2 FOREIGN KEY (login_id) REFERENCES login(id)
);

CREATE TABLE administrador (
	login_id BIGINT,
	PRIMARY KEY(login_id),
	CONSTRAINT administrador_fk1 FOREIGN KEY (login_id) REFERENCES login(id)
);

CREATE TABLE editora (
	nomeeditora VARCHAR(512) NOT NULL,
	idEditora	 BIGSERIAL,
	PRIMARY KEY(idEditora)
);

CREATE TABLE artista (
	nomeartista	 VARCHAR(512) NOT NULL,
	idEditora BIGINT NOT NULL,
	idLogin BIGINT,
	PRIMARY KEY(idLogin),
	CONSTRAINT artista_fk1 FOREIGN KEY (idLogin) REFERENCES pessoa(login_id),
	CONSTRAINT artista_fk2 FOREIGN KEY (idEditora) REFERENCES editora(idEditora)
);

CREATE TABLE som (
	ismn		 VARCHAR(512) NOT NULL,
	titulo		 VARCHAR(512) NOT NULL,
	genero		 VARCHAR(512) NOT NULL,
	datalancamento	 TIMESTAMP NOT NULL,
	duracao		 TIMESTAMP NOT NULL,
	idEditora BIGINT NOT NULL,
	PRIMARY KEY(ismn),
	CONSTRAINT som_fk2 FOREIGN KEY (idEditora) REFERENCES editora(idEditora)
);

CREATE TABLE artista_som (
	idArtista BIGINT,
	som_ismn		 VARCHAR(512),
	PRIMARY KEY(idArtista,som_ismn),
	CONSTRAINT artista_som_fk1 FOREIGN KEY (idArtista) REFERENCES artista(idLogin),
	CONSTRAINT artista_som_fk2 FOREIGN KEY (som_ismn) REFERENCES som(ismn)
);

CREATE TABLE album (
	nome		 VARCHAR(512) NOT NULL,
	datalancamento TIMESTAMP NOT NULL,
	nomeEditora	 VARCHAR(512) NOT NULL,
	idAlbum	 BIGSERIAL,
	PRIMARY KEY(idAlbum)
);

CREATE TABLE ordenarsom (
	ordem	 INT,
	idAlbum BIGINT,
	som_ismn	 VARCHAR(512),
	PRIMARY KEY(ordem,idAlbum,som_ismn),
	CONSTRAINT ordenarsom_fk1 FOREIGN KEY (idAlbum) REFERENCES album(idAlbum),
    CONSTRAINT ordenarsom_fk2 FOREIGN KEY (som_ismn) REFERENCES som(ismn)
);

CREATE TABLE consumidor (
	idPessoa	 BIGINT,
	dataPremium  DATE NOT NULL,
	PRIMARY KEY(idPessoa),
	CONSTRAINT consumidor_playlist_privada_fk2 FOREIGN KEY (idPessoa) REFERENCES pessoa(login_id)
);

CREATE TABLE comentarios (
	comentario	 VARCHAR(512) NOT NULL,
	idcomentario BIGSERIAL NOT NULL,
	idlogin BIGINT NOT NULL,
	som_ismn	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(idcomentario),
	CONSTRAINT comentarios_fk1 FOREIGN KEY (som_ismn) REFERENCES som(ismn),
	CONSTRAINT comentarios_fk2 FOREIGN KEY (idlogin) REFERENCES pessoa(login_id)
);

CREATE TABLE respostaComentarios (
	comentario	 BIGINT,
	resposta BIGINT,
	PRIMARY KEY(comentario, resposta),
	CONSTRAINT comentarios_comentarios_fk1 FOREIGN KEY (comentario) REFERENCES comentarios(idcomentario),
	CONSTRAINT comentarios_comentarios_fk2 FOREIGN KEY (resposta) REFERENCES comentarios(idcomentario)
);

CREATE TABLE giftcards (
	idcartao		 VARCHAR(16),
	datalimite		 TIMESTAMP NOT NULL,
	saldo			 DOUBLE PRECISION NOT NULL,
	idAdmin BIGINT NOT NULL,
	idConsumidor BIGINT,
	PRIMARY KEY(idcartao),
	CONSTRAINT giftcards_fk1 FOREIGN KEY (idAdmin) REFERENCES administrador(login_id),
	CONSTRAINT giftcards_fk2 FOREIGN KEY (idConsumidor) REFERENCES consumidor(idPessoa)
);

CREATE TABLE plano (
	idplano BIGSERIAL,
	duracao VARCHAR(16) NOT NULL,
	preco	 DOUBLE PRECISION NOT NULL,
	PRIMARY KEY(idplano)
);

CREATE TABLE ordemmusicas (
	ordem	 BIGINT,
	som_ismn VARCHAR(512),
	idConsumidor BIGINT,
	PRIMARY KEY(ordem,som_ismn,idConsumidor),
	CONSTRAINT ordemmusicas_fk1 FOREIGN KEY (som_ismn) REFERENCES som(ismn),
	CONSTRAINT ordemmusicas_fk2 FOREIGN KEY (idConsumidor) REFERENCES consumidor(idPessoa)
);

CREATE TABLE atividade (
	id		 BIGSERIAL,
	datavisualizacao TIMESTAMP NOT NULL,
	idConsumidor BIGINT,
	som_ismn VARCHAR(512),
	CONSTRAINT atividade_fk1 FOREIGN KEY (som_ismn) REFERENCES som(ismn),
	CONSTRAINT atividade_fk2 FOREIGN KEY (idConsumidor) REFERENCES consumidor(idPessoa),
	PRIMARY KEY(id)
);

CREATE TABLE subcricao (
	datainicial				 TIMESTAMP NOT NULL,
	idsubcricao				 BIGSERIAL,
	idConsumidor BIGINT,
	plano_idplano				 BIGINT NOT NULL,
	PRIMARY KEY(idsubcricao),
	CONSTRAINT subcricao_fk1 FOREIGN KEY (idConsumidor) REFERENCES consumidor(idPessoa),
	CONSTRAINT subcricao_fk2 FOREIGN KEY (plano_idplano) REFERENCES plano(idplano)
);

CREATE TABLE giftcardutilizado (
	saldoUtilizado BIGINT NOT NULL,
	idCartao VARCHAR(512),
	idSubscricao BIGINT,
	PRIMARY KEY(idCartao,idSubscricao),
	CONSTRAINT giftcardutilizado_fk1 FOREIGN KEY (idCartao) REFERENCES giftcards(idcartao),
	CONSTRAINT giftcardutilizado_fk2 FOREIGN KEY (idSubscricao) REFERENCES subcricao(idsubcricao)
);

CREATE TABLE playlist_publica (
	playlist_idplaylist	 BIGSERIAL NOT NULL,
	playlist_nome	 VARCHAR(512) NOT NULL,
	playlist_datacriacao TIMESTAMP NOT NULL,
	PRIMARY KEY(playlist_idplaylist)
);

CREATE TABLE playlist_privada (
	playlist_idplaylist	 BIGSERIAL NOT NULL,
	playlist_nome	 VARCHAR(512) NOT NULL,
	playlist_datacriacao TIMESTAMP NOT NULL,
	PRIMARY KEY(playlist_idplaylist)
);

CREATE TABLE som_playlist_publica (
	som_ismn				 VARCHAR(512),
	idPlaylist BIGINT,
	PRIMARY KEY(som_ismn,idPlaylist),
	CONSTRAINT som_playlist_publica_fk1 FOREIGN KEY (som_ismn) REFERENCES som(ismn),
	CONSTRAINT som_playlist_publica_fk2 FOREIGN KEY (idPlaylist) REFERENCES playlist_publica(playlist_idplaylist)
);

CREATE TABLE som_playlist_privada (
	som_ismn				 VARCHAR(512),
	idPlaylist BIGINT,
	PRIMARY KEY(som_ismn,idPlaylist),
	CONSTRAINT som_playlist_privada_fk1 FOREIGN KEY (som_ismn) REFERENCES som(ismn),
	CONSTRAINT som_playlist_privada_fk2 FOREIGN KEY (idPlaylist) REFERENCES playlist_privada(playlist_idplaylist)
);

CREATE TABLE consumidor_playlist_privada (
	idPlaylist	 BIGINT,
	idConsumidor BIGINT,
	PRIMARY KEY(idPlaylist,idConsumidor),
	CONSTRAINT playlist_privada_fk1 FOREIGN KEY (idPlaylist) REFERENCES playlist_privada(playlist_idplaylist),
	CONSTRAINT playlist_privada_fk2 FOREIGN KEY (idConsumidor) REFERENCES consumidor(idPessoa)
);

CREATE OR REPLACE FUNCTION activity_trigger() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM ordemmusicas WHERE idconsumidor = NEW.idconsumidor;
    INSERT INTO ordemmusicas(ordem, idconsumidor, som_ismn)
    SELECT RANK() OVER (ORDER BY COUNT(*) DESC), idconsumidor, som_ismn
    FROM atividade
    WHERE idconsumidor = NEW.idconsumidor AND NOW() - NEW.datavisualizacao < (INTERVAL '1 month')
    GROUP BY som_ismn, idconsumidor;
    RETURN NULL;
END;
$$;


CREATE TRIGGER activity_trigger
AFTER INSERT ON atividade
FOR EACH ROW
EXECUTE FUNCTION activity_trigger();

CREATE TABLE consumidor_playlist_publica (
	idPlaylist	 BIGINT,
	idConsumidor BIGINT,
	PRIMARY KEY(idPlaylist,idConsumidor),
	CONSTRAINT playlist_publica_fk1 FOREIGN KEY (idPlaylist) REFERENCES playlist_publica(playlist_idplaylist),
	CONSTRAINT playlist_publica_fk2 FOREIGN KEY (idConsumidor) REFERENCES consumidor(idPessoa)
);

INSERT INTO login(email, password, username) values ('admin1@dei.uc.pt', '12345', 'admin1');

INSERT INTO administrador(login_id) values ('1');

INSERT INTO editora(nomeeditora) values ('Editora1');


