/*CREATE DATABASE nyxdb;*/
CREATE SEQUENCE SQ_ACCOUNTS_PK INCREMENT BY 1 START WITH 1;
CREATE TABLE accounts(
	id INTEGER PRIMARY KEY DEFAULT NEXTVAL('SQ_ACCOUNTS_PK'),
	email VARCHAR(50) UNIQUE NOT NULL,
	hash VARCHAR(64) NOT NULL,
	salt VARCHAR(64) NOT NULL,
	accesslevel INTEGER NOT NULL DEFAULT 3, /*0-root,1-maintence,2-nightclub owner,3-normal*/
	firstname VARCHAR(20) NOT NULL,
	lastname VARCHAR(50) NOT NULL,
	cpf VARCHAR(11) UNIQUE,
	active VARCHAR(6) NOT NULL,
  	timeregistered BIGINT NOT NULL,
  	logintoken VARCHAR(64) DEFAULT 'null'
);
ALTER TABLE accounts ADD CONSTRAINT CK_levels CHECK (accesslevel>=0 AND accesslevel<=3);

CREATE SEQUENCE SQ_RENEWPASS_PK INCREMENT BY 1 START WITH 1;
CREATE TABLE renewpass(
	id INTEGER PRIMARY KEY DEFAULT NEXTVAL('SQ_RENEWPASS_PK'),
	id_accounts INTEGER NOT NULL,
	requesterip VARCHAR(20) NOT NULL,
	modifierip VARCHAR(20),
	token VARCHAR(10) NOT NULL,
	active BOOLEAN NOT NULL DEFAULT true,
	stamp BIGINT NOT NULL
);
ALTER TABLE renewpass ADD CONSTRAINT FK_renewpass_accounts FOREIGN KEY(id_accounts) REFERENCES accounts(id) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE SEQUENCE SQ_NIGHTCLUBS_PK INCREMENT BY 1 START WITH 1;
CREATE TABLE nightclubs(
	id INTEGER PRIMARY KEY DEFAULT NEXTVAL('SQ_NIGHTCLUBS_PK'),
	name VARCHAR(75) NOT NULL,
	cnpj VARCHAR(14) UNIQUE NOT NULL,
	phone VARCHAR(15) NOT NULL,
	email VARCHAR(50) NOT NULL,
	id_address INTEGER NOT NULL,
	id_account INTEGER NOT NULL
);

CREATE SEQUENCE SQ_ADDRESSES_PK INCREMENT BY 1 START WITH 1;
CREATE TABLE addresses(
	id INTEGER PRIMARY KEY DEFAULT NEXTVAL('SQ_ADDRESSES_PK'),
	zipcode INT NOT NULL, 
	street VARCHAR(61) NOT NULL, 
	number INT NOT NULL, 
	xtrainfo VARCHAR(30), 
	district VARCHAR(30) NOT NULL,
	city VARCHAR(30) NOT NULL,
	state VARCHAR(30) NOT NULL,
	country VARCHAR(30) NOT NULL
);
ALTER TABLE nightclubs ADD CONSTRAINT FK_nightclubs_addresses FOREIGN KEY(id_address) REFERENCES addresses(id) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE SEQUENCE SQ_MUSICGENRES_PK INCREMENT BY 1 START WITH 1;
CREATE TABLE musicgenres(
	id INTEGER PRIMARY KEY DEFAULT NEXTVAL('SQ_MUSICGENRES_PK'),
	name VARCHAR(35) NOT NULL
);

CREATE SEQUENCE SQ_EVENTS_PK INCREMENT BY 1 START WITH 1;
CREATE TABLE events(
	id INTEGER PRIMARY KEY DEFAULT NEXTVAL('SQ_EVENTS_PK'),
	name VARCHAR(20) NOT NULL,
	ticketprice NUMERIC(6,2) NOT NULL,
	minimumage SMALLINT NOT NULL,
	startdate BIGINT NOT NULL,
	enddate BIGINT NOT NULL
);

CREATE TABLE eventmusicgenres(
	id_event INTEGER,
	id_genre INTEGER,
	PRIMARY KEY(id_event,id_genre)
);
ALTER TABLE eventmusicgenres ADD CONSTRAINT FK_eventmusicgenres_event FOREIGN KEY(id_event) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE eventmusicgenres ADD CONSTRAINT FK_eventmusicgenres_genre FOREIGN KEY(id_genre) REFERENCES musicgenres(id) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE nightclubevents(
	id_nightclub INTEGER,
	id_event INTEGER,
	PRIMARY KEY(id_nightclub,id_event)
);
ALTER TABLE nightclubevents ADD CONSTRAINT FK_nightclubevents_nightclub FOREIGN KEY(id_nightclub) REFERENCES nightclubs(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE nightclubevents ADD CONSTRAINT FK_nightclubevents_event FOREIGN KEY(id_event) REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE;


INSERT INTO musicgenres ("name") VALUES('Alternativo');
INSERT INTO musicgenres ("name") VALUES('Axé');
INSERT INTO musicgenres ("name") VALUES('Blues');
INSERT INTO musicgenres ("name") VALUES('Bolero');
INSERT INTO musicgenres ("name") VALUES('Bossa Nova');
INSERT INTO musicgenres ("name") VALUES('Brega');
INSERT INTO musicgenres ("name") VALUES('Clássico');
INSERT INTO musicgenres ("name") VALUES('Country');
INSERT INTO musicgenres ("name") VALUES('Cuarteto');
INSERT INTO musicgenres ("name") VALUES('Cumbia');
INSERT INTO musicgenres ("name") VALUES('Dance');
INSERT INTO musicgenres ("name") VALUES('Disco');
INSERT INTO musicgenres ("name") VALUES('Eletrônica');
INSERT INTO musicgenres ("name") VALUES('Emocore');
INSERT INTO musicgenres ("name") VALUES('Fado');
INSERT INTO musicgenres ("name") VALUES('Folk');
INSERT INTO musicgenres ("name") VALUES('Forró');
INSERT INTO musicgenres ("name") VALUES('Funk');
INSERT INTO musicgenres ("name") VALUES('Funk Internacional');
INSERT INTO musicgenres ("name") VALUES('Gospel/Religioso');
INSERT INTO musicgenres ("name") VALUES('Gótico');
INSERT INTO musicgenres ("name") VALUES('Grunge');
INSERT INTO musicgenres ("name") VALUES('Guarânia');
INSERT INTO musicgenres ("name") VALUES('Hard Rock');
INSERT INTO musicgenres ("name") VALUES('Hardcore');
INSERT INTO musicgenres ("name") VALUES('Heavy Metal');
INSERT INTO musicgenres ("name") VALUES('Hip Hop/Rap');
INSERT INTO musicgenres ("name") VALUES('House');
INSERT INTO musicgenres ("name") VALUES('Indie');
INSERT INTO musicgenres ("name") VALUES('Industrial');
INSERT INTO musicgenres ("name") VALUES('Infantil');
INSERT INTO musicgenres ("name") VALUES('Instrumental');
INSERT INTO musicgenres ("name") VALUES('J-Pop/J-Rock');
INSERT INTO musicgenres ("name") VALUES('Jazz');
INSERT INTO musicgenres ("name") VALUES('Jovem Guarda');
INSERT INTO musicgenres ("name") VALUES('K-Pop/K-Rock (ruim pra caralho)');
INSERT INTO musicgenres ("name") VALUES('Mambo');
INSERT INTO musicgenres ("name") VALUES('Marchas/Hinos');
INSERT INTO musicgenres ("name") VALUES('Mariachi');
INSERT INTO musicgenres ("name") VALUES('Merengue');
INSERT INTO musicgenres ("name") VALUES('MPB');
INSERT INTO musicgenres ("name") VALUES('Música andina');
INSERT INTO musicgenres ("name") VALUES('New Age');
INSERT INTO musicgenres ("name") VALUES('New Wave');
INSERT INTO musicgenres ("name") VALUES('Pagode');
INSERT INTO musicgenres ("name") VALUES('Pop');
INSERT INTO musicgenres ("name") VALUES('Pop Rock');
INSERT INTO musicgenres ("name") VALUES('Post-Rock');
INSERT INTO musicgenres ("name") VALUES('Power-Pop');
INSERT INTO musicgenres ("name") VALUES('Rock Progressivo');
INSERT INTO musicgenres ("name") VALUES('Psicodelia');
INSERT INTO musicgenres ("name") VALUES('Punk Rock');
INSERT INTO musicgenres ("name") VALUES('Ranchera');
INSERT INTO musicgenres ("name") VALUES('R&B');
INSERT INTO musicgenres ("name") VALUES('Reggae');
INSERT INTO musicgenres ("name") VALUES('Reggaeton');
INSERT INTO musicgenres ("name") VALUES('Regional');
INSERT INTO musicgenres ("name") VALUES('Rock');
INSERT INTO musicgenres ("name") VALUES('Rock and Roll');
INSERT INTO musicgenres ("name") VALUES('Rockabilly');
INSERT INTO musicgenres ("name") VALUES('Romântico');
INSERT INTO musicgenres ("name") VALUES('Salsa');
INSERT INTO musicgenres ("name") VALUES('Samba');
INSERT INTO musicgenres ("name") VALUES('Samba Enredo');
INSERT INTO musicgenres ("name") VALUES('Sertanejo');
INSERT INTO musicgenres ("name") VALUES('Ska');
INSERT INTO musicgenres ("name") VALUES('Soft Rock');
INSERT INTO musicgenres ("name") VALUES('Soul');
INSERT INTO musicgenres ("name") VALUES('Surf Music');
INSERT INTO musicgenres ("name") VALUES('Tango');
INSERT INTO musicgenres ("name") VALUES('Tecnopop');
INSERT INTO musicgenres ("name") VALUES('Trova');
INSERT INTO musicgenres ("name") VALUES('Velha Guarda');
INSERT INTO musicgenres ("name") VALUES('World Music');
INSERT INTO musicgenres ("name") VALUES('Zamba');
INSERT INTO musicgenres ("name") VALUES('Zouk');

