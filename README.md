# NLP_Recipes
L'obiettivo di questo progetto è l'estrazione, da un testo libero senza alcuna etichettatura, di oggetti ed azioni ad essi correlate relative ad un dato dominio. Gli elementi così ottenuti verranno categorizzati, sempre sulla base del dominio di riferimento, nelle possibili sottocategorie indicate.

## Installazione
Dopo aver clonato il progetto, affiancargli un venv con le librerie necessarie (si consiglia l'uso di Python versione 3.7.9, in quanto al momento non sono state testate altre build del lnguaggio).
Sono richieste due librerie principali:
- SpaCy, versione attualmente testata 3.4.4
- nltk, versione attualmente testata 3.8.1
Sono inoltre richieste le pipeline di riferimento per la libreria SpaCy e il database WordNet (in caso di lingua inglese; per le altre lingue, è richiesto Open Multilingual WordNet) per nltk, ma tali elementi vengono automaticamente scaricati la prima volta che vengono utilizzati.

## Input
Al momento, il progetto riconosce come file in inpt validi solo file in formato json con la seguente struttura. Etichette e invii a capo devono seguire esattamente il seguente schema:
```json
{"Recipes": [
{"Name": "nome ricetta", "Method": "ricetta"},
{"Name": "nome ricetta", "Method": "ricetta"}
]}
```
Come si può osservare, è possibile fornire al progetto più ricette, tra loro scollegate: queste verranno analizzate in serie, ma nessuna separazione verrà effettuata nell'output.

## Utilizzo
La funzione di riferimento per l'elaborazione è la seguente:
```
recipe_extraction(corpus, language, category, results_name_file, silent, info_loop, multi_out, verb_out):
```
- **corpus**: path al corpus file. Deve seguire le specifiche espresse precedentemente.
- **language**: lingua di riferimento per il progetto. Una lista esaustiva delle possibili lingue attualmente implementate è reperibile nel file "constants.py" sotto il dizionario LANG.
- **category**: dominio da usare durante la fase di categorizzazione. Una lista esaustiva dei domini implementati è reperibile nel file "constants.py", sotto il dizionario CATEGORIES.
- **results_name_file**: nome richiesto per il file di output, o intero path ad esso. Non deve comprendere un'estensione. Per default, il file avrà nome "output" e sarà creato nella cartella Output del progetto. Specificare solo un nome del file lo creerà nella caretlla Main: usare invece "Output/nome_desiderato" per mantenere il normale risultato.
- **silent**: flag per abilitare o disabilitare il testo di controllo sul terminale durante l'elaborazione. True disabilita tale testo. _Default: False_.
- **info_loop**: valutata solo se _"**silent**=False"_, indica ogni quanti elementi viene stampata una frase di supporto nei cicli del progetto. Utilizzato principalmente per elaborazioni particolarmente consistenti. _Default: 1000_.
- **multi_out**: flag per restituire l'output in due differenti costruzioni (e formati). True restituisce una versione verbosa (formato txt) ed una più strutturata (formato json). _Default: False_
- **verb_out**: flag valutato solo se _"**multi_out**=False"_. Seleziona quale delle due versioni dell'output viene generata:
  - "True" rende la forma verbosa (formato txt)
  - "False" (il default) rende la versione struttrata (formato json)

## Estensioni del progetto
È possibile estendere il progetto perché copra domini diversi da quelli presenti o lavori in lingue differenti da quelle implementate. In entrambi i casi, le modifiche devono essere apportate nel file "constants.py".

Per aggiungere una nuova lingua non supportata, aggiungere una nuova voce al dizionario LANG, usando come identificatore un codice a due lettere per la lingua (esempi presenti sono EN per l'inglese e IT per l'italiano) seguito da un numero progressivo (in modo da poter impostare più versioni per la stessa lingua). Gli attributi da inserire suano gli identificatori "spaCy" e "nltk" e sono, rispettivamente, il nome della pipeline spaCy per la lingua e l'attributo linguistico per OMW.

Per aggiungere una nuova lingua ad un dominio esistente, assicurarsi prima di tutto che tale lingua esista nel dizionario LANG. Dopodiché, aggiungere un nuovo dizionario all'interno del dominio esistente (CATEGORIES è un dizionario di dizionari, dove il livello superiore sono i diversi domini, mentre l'inferioe le singole lingue), usando come identificatore lo stesso della lingua (senza numero progressivo) presente in LANG. Si consiglia di verificare i lemmi riconosciuti da WordNet.

Per aggiungere un dominio completamente nuovo, la procedura è simile alla precedente, ma va aggiunto un dizionario in CATEGORIES dal livello superiore. Una volta creato un nuovo dizionario, con identificatore pari al nome da utilizzare per il dominio, aggiungere un sotto-dizionario apposito per la lingua in cui si vuole effettuare l'analisi secondo le regole riportate sopra.
