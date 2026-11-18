# Metodologia delle simulazioni

Gli importi sono in euro. I grafici e i file Excel mantengono la precisione dei calcoli. Gli indicatori riepilogativi arrotondano gli importi all’euro.

## Casa o affitto

Entrambi gli scenari partono con lo stesso capitale iniziale e lo stesso budget mensile prima delle spese abitative.

- **Affitto.** Il capitale iniziale viene investito. A fine mese si investe la differenza tra il budget e il canone.
- **Acquisto.** Anticipo e spese iniziali riducono il capitale da investire. A fine mese si investe la differenza tra il budget, la rata e le spese di proprietà. Dopo l’ultima rata si sottraggono solo le spese di proprietà. Il patrimonio include il portafoglio e il valore della casa al netto del debito residuo.

Il calcolo richiede che il capitale copra anticipo e costi iniziali e che il budget copra entrambe le spese mensili. Il rendimento dell’investimento è un tasso annuo effettivo convertito al tasso mensile equivalente. La casa si rivaluta al tasso annuo indicato. Per ottenere gli euro di oggi, il capitale di ogni anno viene diviso per `(1 + inflazione)^anni`.

Affitto e spese di proprietà restano fissi. Il modello assume un mutuo a tasso fisso ed esclude i costi di vendita e la tassazione dei rendimenti. Non considera il valore d’uso dell’immobile o le differenze di qualità fra le alternative.

## Prestiti e mutui

Il calcolo usa il piano a rata costante con tasso mensile pari al tasso nominale annuo diviso per 12. A tasso zero, la rata base è il capitale diviso per il numero di mesi.

Ogni rata copre prima gli interessi maturati nel mese. Il resto della rata e il versamento extra riducono il capitale. Nell’ultimo mese il pagamento è limitato al capitale residuo più l’interesse dovuto. Il confronto usa lo stesso finanziamento con extra pari a zero. Il calcolo esclude commissioni, assicurazioni e penali.

## Pensione

Il rendimento nominale positivo è ridotto dall’aliquota ipotetica indicata. Il rendimento netto è convertito al tasso mensile equivalente. I versamenti ricorrenti entrano a fine mese e l’eventuale versamento extra entra al termine di ogni anno.

Il capitale reale è il capitale nominale diviso per `(1 + inflazione)^anni`. La copertura stimata divide il capitale reale alla pensione per la spesa annua in euro di oggi e assume rendimenti reali nulli dopo il pensionamento. Con prelievo nullo l’app mostra **Nessun prelievo**. Il modello esclude prestazioni previdenziali e variazioni dei rendimenti nel tempo.

## Dati e sessione

I simulatori elaborano gli input nel processo Streamlit. L’app genera il file Excel in memoria. I riepiloghi disponibili nella chat appartengono alla sessione e vengono condivisi con OpenAI quando selezionati e quando l’utente invia una domanda. La cronologia recente può contenere risposte basate su riepiloghi inviati in precedenza. Per ripartire senza quella cronologia usa **Nuova chat**.
