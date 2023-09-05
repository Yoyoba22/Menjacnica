CREATE TABLE Kursna_lista(
valute VARCHAR(5) PRIMARY KEY NOT NULL,
iznos_valute FLOAT NOT NULL,
iznos_valute_dinar FLOAT NOT NULL);

DROP TABLE Kursna_lista
SELECT * FROM Kursna_lista

CREATE TABLE Transakcija(
sifra_transakcije SERIAL NOT NULL,
iz_koje_valute VARCHAR(5) NOT NULL,
u_valutu VARCHAR(5) NOT NULL,
iznos_konvertovano FLOAT NOT NULL,
iznos_posle_konverzije FLOAT,
PRIMARY KEY(sifra_transakcije),
FOREIGN KEY(iz_koje_valute) REFERENCES Kursna_lista(valute),
FOREIGN KEY(u_valutu) REFERENCES Kursna_lista(valute));

DROP TABLE Transakcija

SELECT * FROM Transakcija

INSERT INTO Transakcija (sifra_transakcije,iz_koje_valute,u_valutu,iznos_konvertovano,iznos_posle_konverzije)
VALUES
		(1,'DIN','USD',1500,0),
		(2,'USD','DIN',100,0),
		(3,'DIN','CHF',2500,0),
		(4,'GBP','DIN',50,0);



UPDATE Transakcija t
SET iznos_posle_konverzije = CASE
    WHEN t.u_valutu != 'DIN' THEN t.iznos_konvertovano / k.iznos_valute_dinar
    WHEN t.iz_koje_valute != 'DIN' THEN t.iznos_konvertovano * k.iznos_valute_dinar
    ELSE t.iznos_posle_konverzije -- Optionally, handle the 'DIN' case here
END
FROM Kursna_lista k
WHERE (t.u_valutu != 'DIN' AND k.valute = t.u_valutu) OR
      (t.iz_koje_valute != 'DIN' AND k.valute = t.iz_koje_valute);