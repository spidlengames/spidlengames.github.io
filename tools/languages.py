"""Makes the translated pages from the English ones.

The English pages are the originals: index.html, cannonball-captains/index.html and
cannonball-captains/privacy/index.html. Each other language gets a copy one folder down
(cs/cannonball-captains/index.html and so on) with the texts below swapped in, links to shared
files (styles, pictures, the browser game) fixed, and its own screenshots. Every page also gets
the language picker (top right) and links telling search engines about the other languages.

After changing an English page, add or update its texts in TEXTS and run:

    python3 tools/languages.py

It reports texts it couldn't find, which usually means an English text changed.
"""

import os
import posixpath
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SITE = "https://spidlengames.github.io/"
LANGUAGES = [("en", "English"), ("cs", "Čeština"), ("de", "Deutsch"), ("fr", "Français"), ("it", "Italiano")]
PAGES = ["index.html", "cannonball-captains/index.html", "cannonball-captains/privacy/index.html"]
# Files every language shares; translated pages reach them one folder further up.
SHARED = ("assets/", "cannonball-captains/play/")
# Screenshots exist for every language (assets/img/screens/<language>/).
SCREENS = "assets/img/screens/"
GLOBE = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2">'
         '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/></svg>')

# English, Czech, German, French, Italian. A text may include HTML; spaces and line breaks in the
# English match any spacing in the page.
TEXTS = [
    # ---- Shared bits ----
    ("Spidlen Games makes small, friendly games for families. No ads, no tracking, just fun.",
     "Spidlen Games dělá malé, přátelské hry pro rodiny. Bez reklam, bez sledování, jen zábava.",
     "Spidlen Games macht kleine, freundliche Spiele für Familien. Keine Werbung, kein Tracking, nur Spaß.",
     "Spidlen Games crée de petits jeux sympas pour toute la famille. Sans pub, sans pistage, juste pour s'amuser.",
     "Spidlen Games crea piccoli giochi simpatici per le famiglie. Niente pubblicità, niente tracciamento, solo divertimento."),
    ("Small, friendly games for families.", "Malé, přátelské hry pro rodiny.", "Kleine, freundliche Spiele für Familien.",
     "De petits jeux sympas pour toute la famille.", "Piccoli giochi simpatici per le famiglie."),
    ('<a href="#games">Games</a>', '<a href="#games">Hry</a>', '<a href="#games">Spiele</a>', '<a href="#games">Jeux</a>', '<a href="#games">Giochi</a>'),
    ('<a href="#about">About</a>', '<a href="#about">O nás</a>', '<a href="#about">Über uns</a>', '<a href="#about">À propos</a>', '<a href="#about">Chi siamo</a>'),
    ('alt="Cannonball Captains title screen"', 'alt="Úvodní obrazovka Cannonball Captains"', 'alt="Startbildschirm von Cannonball Captains"',
     'alt="Écran d\'accueil de Cannonball Captains"', 'alt="Schermata iniziale di Cannonball Captains"'),
    ("Small games · big fun", "Malé hry · velká zábava", "Kleine Spiele · großer Spaß", "Petits jeux · grand plaisir", "Piccoli giochi · grande divertimento"),
    ("Friendly, colorful games for kids and grown-ups to play together. No ads, no tracking, no in-app purchases. Just play.",
     "Přátelské, barevné hry, které hrají děti i dospělí spolu. Bez reklam, bez sledování, bez nákupů ve hře. Prostě hrajte.",
     "Freundliche, bunte Spiele für Kinder und Erwachsene zum gemeinsamen Spielen. Keine Werbung, kein Tracking, keine In-App-Käufe. Einfach spielen.",
     "Des jeux colorés et sympas, à partager entre enfants et adultes. Sans pub, sans pistage, sans achats intégrés. Il n'y a qu'à jouer.",
     "Giochi colorati e simpatici per bambini e adulti, da giocare insieme. Niente pubblicità, niente tracciamento, niente acquisti in-app. Solo gioco."),
    ("Meet Cannonball Captains", "Seznamte se s Cannonball Captains", "Lerne Cannonball Captains kennen", "Découvrez Cannonball Captains", "Scopri Cannonball Captains"),
    ("<h2>Our games</h2>", "<h2>Naše hry</h2>", "<h2>Unsere Spiele</h2>", "<h2>Nos jeux</h2>", "<h2>I nostri giochi</h2>"),
    ("A cartoon sea battle for Android and the web. Hide your fleet, fire cannonballs, and sink the enemy ships before they sink yours! Play the computer or a friend online.",
     "Kreslená námořní bitva pro Android a web. Schovej svou flotilu, pal dělovými koulemi a potop nepřátelské lodě dřív, než potopí ty tvoje! Hraj proti počítači nebo s kamarádem online.",
     "Eine Seeschlacht im Cartoon-Stil für Android und das Web. Versteck deine Flotte, feuere Kanonenkugeln ab und versenke die feindlichen Schiffe, bevor sie deine versenken! Spiel gegen den Computer oder online mit Freunden.",
     "Une bataille navale façon dessin animé, pour Android et le Web. Cache ta flotte, tire des boulets de canon et coule les navires ennemis avant qu'ils ne coulent les tiens ! Joue contre l'ordinateur ou avec un ami en ligne.",
     "Una battaglia navale a cartoni animati per Android e il Web. Nascondi la tua flotta, spara palle di cannone e affonda le navi nemiche prima che affondino le tue! Gioca contro il computer o con un amico online."),
    ("More on the way", "Další na cestě", "Mehr ist unterwegs", "D'autres arrivent", "Altri in arrivo"),
    ("We're always dreaming up the next adventure.", "Pořád vymýšlíme další dobrodružství.", "Wir träumen schon vom nächsten Abenteuer.",
     "Nous imaginons déjà la prochaine aventure.", "Stiamo già sognando la prossima avventura."),
    ("<h2>About us</h2>", "<h2>O nás</h2>", "<h2>Über uns</h2>", "<h2>À propos</h2>", "<h2>Chi siamo</h2>"),
    ("Spidlen Games is a tiny family studio. We make the kind of games we want to play with our own kids: simple to learn, fun to share, and kind to your privacy.",
     "Spidlen Games je malé rodinné studio. Děláme takové hry, jaké chceme hrát se svými dětmi: snadno se naučí, baví ve společnosti a šetří vaše soukromí.",
     "Spidlen Games ist ein winziges Familienstudio. Wir machen die Spiele, die wir mit unseren eigenen Kindern spielen wollen: leicht zu lernen, schön zum Teilen und freundlich zu deiner Privatsphäre.",
     "Spidlen Games est un tout petit studio familial. Nous faisons les jeux auxquels nous voulons jouer avec nos propres enfants : faciles à apprendre, amusants à partager et respectueux de votre vie privée.",
     "Spidlen Games è un piccolo studio di famiglia. Facciamo i giochi che vogliamo giocare con i nostri figli: facili da imparare, belli da condividere e rispettosi della tua privacy."),
    ("Cannonball Captains privacy policy", "Zásady ochrany soukromí Cannonball Captains", "Datenschutzerklärung von Cannonball Captains",
     "Politique de confidentialité de Cannonball Captains", "Informativa sulla privacy di Cannonball Captains"),

    # ---- Cannonball Captains ----
    ("Cannonball Captains: a cartoon sea battle for Android and the web. Hide your fleet, fire cannonballs and sink the enemy ships. Play the computer or a friend online. Free, no ads.",
     "Cannonball Captains: kreslená námořní bitva pro Android a web. Schovej flotilu, pal dělovými koulemi a potop nepřátelské lodě. Hraj proti počítači nebo s kamarádem online. Zdarma, bez reklam.",
     "Cannonball Captains: eine Seeschlacht im Cartoon-Stil für Android und das Web. Versteck deine Flotte, feuere Kanonenkugeln ab und versenke die feindlichen Schiffe. Gegen den Computer oder online mit Freunden. Kostenlos, ohne Werbung.",
     "Cannonball Captains : une bataille navale façon dessin animé, pour Android et le Web. Cache ta flotte, tire des boulets de canon et coule les navires ennemis. Contre l'ordinateur ou avec un ami en ligne. Gratuit, sans pub.",
     "Cannonball Captains: una battaglia navale a cartoni animati per Android e il Web. Nascondi la flotta, spara palle di cannone e affonda le navi nemiche. Contro il computer o con un amico online. Gratis, senza pubblicità."),
    ("A cartoon sea battle for Android. Free, no ads.", "Kreslená námořní bitva pro Android. Zdarma, bez reklam.", "Eine Cartoon-Seeschlacht für Android. Kostenlos, ohne Werbung.",
     "Une bataille navale façon dessin animé pour Android. Gratuit, sans pub.", "Una battaglia navale a cartoni animati per Android. Gratis, senza pubblicità."),
    ('<a href="#features">Features</a>', '<a href="#features">Co umí</a>', '<a href="#features">Funktionen</a>', '<a href="#features">Points forts</a>', '<a href="#features">Caratteristiche</a>'),
    ('<a href="#screens">Screenshots</a>', '<a href="#screens">Obrázky</a>', '<a href="#screens">Bilder</a>', '<a href="#screens">Captures</a>', '<a href="#screens">Immagini</a>'),
    ('<a href="#download">Download</a>', '<a href="#download">Stáhnout</a>', '<a href="#download">Download</a>', '<a href="#download">Télécharger</a>', '<a href="#download">Scarica</a>'),
    ('<a href="privacy/">Privacy</a>', '<a href="privacy/">Soukromí</a>', '<a href="privacy/">Datenschutz</a>', '<a href="privacy/">Confidentialité</a>', '<a href="privacy/">Privacy</a>'),
    ('alt="Cannonball Captains icon"', 'alt="Ikona Cannonball Captains"', 'alt="Symbol von Cannonball Captains"', 'alt="Icône de Cannonball Captains"', 'alt="Icona di Cannonball Captains"'),
    ("Hide your fleet, fire cannonballs, and sink the enemy ships before they sink yours! A cartoon sea battle for the whole family.",
     "Schovej svou flotilu, pal dělovými koulemi a potop nepřátelské lodě dřív, než potopí ty tvoje! Kreslená námořní bitva pro celou rodinu.",
     "Versteck deine Flotte, feuere Kanonenkugeln ab und versenke die feindlichen Schiffe, bevor sie deine versenken! Eine Cartoon-Seeschlacht für die ganze Familie.",
     "Cache ta flotte, tire des boulets de canon et coule les navires ennemis avant qu'ils ne coulent les tiens ! Une bataille navale façon dessin animé pour toute la famille.",
     "Nascondi la tua flotta, spara palle di cannone e affonda le navi nemiche prima che affondino le tue! Una battaglia navale a cartoni animati per tutta la famiglia."),
    ('href="#download">Download for Android</a>', 'href="#download">Stáhnout pro Android</a>', 'href="#download">Für Android herunterladen</a>',
     'href="#download">Télécharger pour Android</a>', 'href="#download">Scarica per Android</a>'),
    (">Play in your browser</a>", ">Hrát v prohlížeči</a>", ">Im Browser spielen</a>", ">Jouer dans le navigateur</a>", ">Gioca nel browser</a>"),
    ("Free · No ads · No in-app purchases", "Zdarma · Bez reklam · Bez nákupů ve hře", "Kostenlos · Keine Werbung · Keine In-App-Käufe",
     "Gratuit · Sans pub · Sans achats intégrés", "Gratis · Niente pubblicità · Niente acquisti in-app"),
    ('alt="A ship being sunk in battle"', 'alt="Loď jde v bitvě ke dnu"', 'alt="Ein Schiff wird in der Schlacht versenkt"',
     'alt="Un navire coulé pendant la bataille"', 'alt="Una nave affondata in battaglia"'),
    ("Ahoy, captain!", "Ahoj, kapitáne!", "Ahoi, Kapitän!", "Ohé, capitaine !", "Ehilà, capitano!"),
    ("<h3>Play alone</h3>", "<h3>Hraj sólo</h3>", "<h3>Allein spielen</h3>", "<h3>Joue en solo</h3>", "<h3>Gioca in solitario</h3>"),
    ("Take on the computer: an easy Cadet, a crafty Captain, or a tough Admiral who thinks like a pro.",
     "Utkej se s počítačem: snadným Kadetem, mazaným Kapitánem nebo tvrdým Admirálem, který přemýšlí jako profík.",
     "Tritt gegen den Computer an: einen leichten Kadetten, einen schlauen Kapitän oder einen harten Admiral, der wie ein Profi denkt.",
     "Affronte l'ordinateur : un Cadet facile, un Capitaine rusé ou un Amiral coriace qui réfléchit comme un pro.",
     "Sfida il computer: un Cadetto facile, un Capitano astuto o un Ammiraglio tosto che ragiona come un esperto."),
    ("<h3>Play with a friend</h3>", "<h3>Hraj s kamarádem</h3>", "<h3>Mit Freunden spielen</h3>", "<h3>Joue avec un ami</h3>", "<h3>Gioca con un amico</h3>"),
    ("Each on your own phone or tablet, anywhere with internet. Share a 4-letter code and battle it out.",
     "Každý na svém telefonu nebo tabletu, kdekoli s internetem. Pošlete si čtyřpísmenný kód a do boje!",
     "Jeder auf seinem eigenen Handy oder Tablet, überall mit Internet. Teilt einen Code aus 4 Buchstaben und los geht die Schlacht.",
     "Chacun sur son téléphone ou sa tablette, partout où il y a Internet. Partagez un code de 4 lettres et que la bataille commence !",
     "Ognuno sul proprio telefono o tablet, ovunque ci sia Internet. Condividete un codice di 4 lettere e che la battaglia abbia inizio!"),
    ("<h3>Pick your captain</h3>", "<h3>Vyber si kapitána</h3>", "<h3>Wähle deinen Kapitän</h3>", "<h3>Choisis ton capitaine</h3>", "<h3>Scegli il tuo capitano</h3>"),
    ("Choose from 32 cartoon characters, from pirates and mermaids to narwhals and lighthouses. Count your wins!",
     "Vybírej z 32 kreslených postaviček, od pirátů a mořských panen po narvaly a majáky. Počítej svoje výhry!",
     "Wähle aus 32 Cartoon-Figuren, von Piraten und Meerjungfrauen bis zu Narwalen und Leuchttürmen. Zähl deine Siege!",
     "Choisis parmi 32 personnages, des pirates et sirènes aux narvals et phares. Compte tes victoires !",
     "Scegli tra 32 personaggi a cartoni animati, da pirati e sirene a narvali e fari. Conta le tue vittorie!"),
    ("<h3>Splash and boom</h3>", "<h3>Šplouch a bum</h3>", "<h3>Platsch und Bumm</h3>", "<h3>Plouf et boum</h3>", "<h3>Splash e bum</h3>"),
    ("Flying cannonballs, big splashes, fiery hits and sinking ships, with sound effects to match.",
     "Létající dělové koule, velké šplouchance, ohnivé zásahy a potápějící se lodě, a k tomu zvuky.",
     "Fliegende Kanonenkugeln, große Platscher, feurige Treffer und sinkende Schiffe, mit passenden Soundeffekten.",
     "Boulets qui volent, grosses éclaboussures, coups enflammés et navires qui sombrent, avec les bruitages qui vont avec.",
     "Palle di cannone in volo, grandi spruzzi, colpi infuocati e navi che affondano, con gli effetti sonori giusti."),
    ("<h3>Fair play built in</h3>", "<h3>Férová hra</h3>", "<h3>Fair Play eingebaut</h3>", "<h3>Franc-jeu garanti</h3>", "<h3>Gioco leale garantito</h3>"),
    ("At the end of an online game, each device checks the other captain's fleet. No cheating!",
     "Na konci online hry každé zařízení zkontroluje flotilu druhého kapitána. Žádné podvádění!",
     "Am Ende eines Online-Spiels prüft jedes Gerät die Flotte des anderen Kapitäns. Kein Schummeln!",
     "À la fin d'une partie en ligne, chaque appareil vérifie la flotte de l'autre capitaine. Pas de triche !",
     "Alla fine di una partita online, ogni dispositivo controlla la flotta dell'altro capitano. Niente imbrogli!"),
    ("<h3>Kind to your privacy</h3>", "<h3>Šetrná k soukromí</h3>", "<h3>Freundlich zur Privatsphäre</h3>", "<h3>Respect de la vie privée</h3>", "<h3>Rispetto della privacy</h3>"),
    ('No ads, no tracking, no account to sign up for. <a href="privacy/">Read our privacy policy.</a>',
     'Bez reklam, bez sledování, bez registrace. <a href="privacy/">Přečti si zásady ochrany soukromí.</a>',
     'Keine Werbung, kein Tracking, kein Konto nötig. <a href="privacy/">Lies unsere Datenschutzerklärung.</a>',
     'Sans pub, sans pistage, sans compte à créer. <a href="privacy/">Lis notre politique de confidentialité.</a>',
     'Niente pubblicità, niente tracciamento, nessun account da creare. <a href="privacy/">Leggi la nostra informativa sulla privacy.</a>'),
    ('<h2 class="center">Screenshots</h2>', '<h2 class="center">Obrázky ze hry</h2>', '<h2 class="center">Bilder aus dem Spiel</h2>',
     '<h2 class="center">Captures d\'écran</h2>', '<h2 class="center">Immagini dal gioco</h2>'),
    ('alt="Title screen"', 'alt="Úvodní obrazovka"', 'alt="Startbildschirm"', 'alt="Écran d\'accueil"', 'alt="Schermata iniziale"'),
    ("<figcaption>Choose how to play</figcaption>", "<figcaption>Vyber si, jak hrát</figcaption>", "<figcaption>Wähle, wie du spielst</figcaption>",
     "<figcaption>Choisis comment jouer</figcaption>", "<figcaption>Scegli come giocare</figcaption>"),
    ('alt="Placing the fleet"', 'alt="Rozmísťování flotily"', 'alt="Die Flotte platzieren"', 'alt="Placement de la flotte"', 'alt="Posizionare la flotta"'),
    ("<figcaption>Hide your fleet</figcaption>", "<figcaption>Schovej flotilu</figcaption>", "<figcaption>Versteck deine Flotte</figcaption>",
     "<figcaption>Cache ta flotte</figcaption>", "<figcaption>Nascondi la flotta</figcaption>"),
    ('alt="Sinking a ship"', 'alt="Potápění lodi"', 'alt="Ein Schiff versenken"', 'alt="Un navire qui coule"', 'alt="Affondare una nave"'),
    ("<figcaption>Sink their ships</figcaption>", "<figcaption>Potop jejich lodě</figcaption>", "<figcaption>Versenke ihre Schiffe</figcaption>",
     "<figcaption>Coule leurs navires</figcaption>", "<figcaption>Affonda le loro navi</figcaption>"),
    ('alt="A splash"', 'alt="Šplouchnutí"', 'alt="Ein Platscher"', 'alt="Une éclaboussure"', 'alt="Uno spruzzo"'),
    ("<figcaption>Splash! A miss</figcaption>", "<figcaption>Šplouch! Vedle</figcaption>", "<figcaption>Platsch! Daneben</figcaption>",
     "<figcaption>Plouf ! Raté</figcaption>", "<figcaption>Splash! Mancato</figcaption>"),
    ('alt="Captains"', 'alt="Kapitáni"', 'alt="Kapitäne"', 'alt="Capitaines"', 'alt="Capitani"'),
    ("<figcaption>Your captains</figcaption>", "<figcaption>Tvoji kapitáni</figcaption>", "<figcaption>Deine Kapitäne</figcaption>",
     "<figcaption>Tes capitaines</figcaption>", "<figcaption>I tuoi capitani</figcaption>"),
    ('alt="Characters"', 'alt="Postavičky"', 'alt="Figuren"', 'alt="Personnages"', 'alt="Personaggi"'),
    ("<figcaption>32 characters</figcaption>", "<figcaption>32 postaviček</figcaption>", "<figcaption>32 Figuren</figcaption>",
     "<figcaption>32 personnages</figcaption>", "<figcaption>32 personaggi</figcaption>"),
    ("<h2>Download</h2>", "<h2>Stáhnout</h2>", "<h2>Herunterladen</h2>", "<h2>Télécharger</h2>", "<h2>Scarica</h2>"),
    ("For Android phones and tablets (Android 7 or newer), including Amazon Fire tablets. Coming to Google Play soon.",
     "Pro telefony a tablety s Androidem (Android 7 nebo novější), včetně tabletů Amazon Fire. Brzy i na Google Play.",
     "Für Android-Handys und -Tablets (Android 7 oder neuer), auch Amazon-Fire-Tablets. Bald auch bei Google Play.",
     "Pour les téléphones et tablettes Android (Android 7 ou plus récent), y compris les tablettes Amazon Fire. Bientôt sur Google Play.",
     "Per telefoni e tablet Android (Android 7 o successivo), compresi i tablet Amazon Fire. Presto anche su Google Play."),
    ('Download <small id="download-version">version ', 'Stáhnout <small id="download-version">verze ', 'Herunterladen <small id="download-version">Version ',
     'Télécharger <small id="download-version">version ', 'Scarica <small id="download-version">versione '),
    (">All versions</a>", ">Všechny verze</a>", ">Alle Versionen</a>", ">Toutes les versions</a>", ">Tutte le versioni</a>"),
    ("No Android? Play in your browser", "Nemáš Android? Hraj v prohlížeči", "Kein Android? Spiel im Browser", "Pas d'Android ? Joue dans le navigateur", "Niente Android? Gioca nel browser"),
    ("The same game runs right in a web browser on a computer, tablet or phone, with nothing to install. It plays online with the Android app too. The first visit downloads about 12 MB.",
     "Stejná hra běží přímo ve webovém prohlížeči na počítači, tabletu i telefonu, nic se neinstaluje. Online hraje i s aplikací pro Android. Při první návštěvě se stáhne asi 12 MB.",
     "Dasselbe Spiel läuft direkt im Webbrowser auf Computer, Tablet oder Handy, ohne Installation. Online spielt es auch mit der Android-App zusammen. Beim ersten Besuch werden etwa 12 MB geladen.",
     "Le même jeu fonctionne directement dans un navigateur, sur ordinateur, tablette ou téléphone, sans rien installer. En ligne, il joue aussi avec l'appli Android. La première visite télécharge environ 12 Mo.",
     "Lo stesso gioco funziona direttamente nel browser, su computer, tablet o telefono, senza installare nulla. Online gioca anche con l'app Android. La prima visita scarica circa 12 MB."),
    ("<h3>How to install</h3>", "<h3>Jak nainstalovat</h3>", "<h3>So installierst du es</h3>", "<h3>Comment l'installer</h3>", "<h3>Come installarlo</h3>"),
    ("<strong>Download the file</strong> on your Android phone or tablet. If your browser asks whether to keep it, choose <strong>Download anyway</strong>.",
     "<strong>Stáhni soubor</strong> do telefonu nebo tabletu s Androidem. Pokud se prohlížeč zeptá, jestli ho ponechat, zvol <strong>Přesto stáhnout</strong>.",
     "<strong>Lade die Datei</strong> auf dein Android-Handy oder -Tablet. Wenn der Browser fragt, ob du sie behalten willst, wähle <strong>Trotzdem herunterladen</strong>.",
     "<strong>Télécharge le fichier</strong> sur ton téléphone ou ta tablette Android. Si le navigateur demande s'il faut le conserver, choisis <strong>Télécharger quand même</strong>.",
     "<strong>Scarica il file</strong> sul tuo telefono o tablet Android. Se il browser chiede se tenerlo, scegli <strong>Scarica comunque</strong>."),
    ("<strong>Open it and tap Install.</strong> If Android says it can't install apps from this source, tap <strong>Settings</strong>, switch on <strong>Allow from this source</strong>, then go back and tap <strong>Install</strong>.",
     "<strong>Otevři ho a klepni na Instalovat.</strong> Pokud Android hlásí, že z tohoto zdroje nemůže instalovat aplikace, klepni na <strong>Nastavení</strong>, zapni <strong>Povolit z tohoto zdroje</strong>, vrať se a klepni na <strong>Instalovat</strong>.",
     "<strong>Öffne sie und tippe auf Installieren.</strong> Wenn Android meldet, dass es aus dieser Quelle keine Apps installieren kann, tippe auf <strong>Einstellungen</strong>, schalte <strong>Dieser Quelle vertrauen</strong> ein, geh zurück und tippe auf <strong>Installieren</strong>.",
     "<strong>Ouvre-le et touche Installer.</strong> Si Android dit qu'il ne peut pas installer d'applis de cette source, touche <strong>Paramètres</strong>, active <strong>Autoriser cette source</strong>, puis reviens et touche <strong>Installer</strong>.",
     "<strong>Aprilo e tocca Installa.</strong> Se Android dice che non può installare app da questa fonte, tocca <strong>Impostazioni</strong>, attiva <strong>Consenti da questa fonte</strong>, poi torna indietro e tocca <strong>Installa</strong>."),
    ('<strong>Google Play Protect may call it "unrecognized".</strong> That\'s normal for apps that aren\'t from the Play Store. Choose <strong>Scan app</strong>, or <strong>More details → Install anyway</strong>.',
     "<strong>Google Play Protect ji může označit za „nerozpoznanou“.</strong> To je u aplikací mimo Obchod Play normální. Zvol <strong>Zkontrolovat aplikaci</strong> nebo <strong>Další podrobnosti → Přesto nainstalovat</strong>.",
     "<strong>Google Play Protect nennt sie vielleicht „unbekannt“.</strong> Das ist bei Apps außerhalb des Play Store normal. Wähle <strong>App scannen</strong> oder <strong>Weitere Details → Trotzdem installieren</strong>.",
     "<strong>Google Play Protect peut la dire « non reconnue ».</strong> C'est normal pour les applis qui ne viennent pas du Play Store. Choisis <strong>Analyser l'appli</strong>, ou <strong>Plus d'informations → Installer quand même</strong>.",
     "<strong>Google Play Protect potrebbe definirla «non riconosciuta».</strong> È normale per le app che non vengono dal Play Store. Scegli <strong>Scansiona app</strong> oppure <strong>Altri dettagli → Installa comunque</strong>."),
    ("<strong>Open Cannonball Captains</strong>, make a captain, and set sail!",
     "<strong>Otevři Cannonball Captains</strong>, vytvoř si kapitána a vypluj!",
     "<strong>Öffne Cannonball Captains</strong>, leg einen Kapitän an und stich in See!",
     "<strong>Ouvre Cannonball Captains</strong>, crée un capitaine et lève l'ancre !",
     "<strong>Apri Cannonball Captains</strong>, crea un capitano e salpa!"),
    ("<strong>Amazon Fire tablets:</strong> allow installing under <em>Settings → Security &amp; Privacy → Apps from Unknown Sources</em> for the app you downloaded with. <strong>Updating:</strong> install the new file over the old one. Your captains and wins are kept.",
     "<strong>Tablety Amazon Fire:</strong> instalaci povol v <em>Nastavení → Zabezpečení a soukromí → Aplikace z neznámých zdrojů</em> pro aplikaci, kterou jsi soubor stáhl(a). <strong>Aktualizace:</strong> nový soubor nainstaluj přes starý. Kapitáni i výhry zůstanou.",
     "<strong>Amazon-Fire-Tablets:</strong> Erlaube die Installation unter <em>Einstellungen → Sicherheit &amp; Datenschutz → Apps aus unbekannten Quellen</em> für die App, mit der du heruntergeladen hast. <strong>Aktualisieren:</strong> Installiere die neue Datei über die alte. Deine Kapitäne und Siege bleiben erhalten.",
     "<strong>Tablettes Amazon Fire :</strong> autorise l'installation dans <em>Paramètres → Sécurité et confidentialité → Applis de sources inconnues</em> pour l'appli qui a servi au téléchargement. <strong>Mise à jour :</strong> installe le nouveau fichier par-dessus l'ancien. Tes capitaines et tes victoires sont conservés.",
     "<strong>Tablet Amazon Fire:</strong> consenti l'installazione in <em>Impostazioni → Sicurezza e privacy → App da fonti sconosciute</em> per l'app con cui hai scaricato il file. <strong>Aggiornare:</strong> installa il nuovo file sopra quello vecchio. I tuoi capitani e le vittorie restano."),
    ("<h2>How to play</h2>", "<h2>Jak hrát</h2>", "<h2>So wird gespielt</h2>", "<h2>Comment jouer</h2>", "<h2>Come si gioca</h2>"),
    ("<strong>Place your fleet.</strong> Every captain has 5 ships: a Carrier (5 squares), a Battleship (4), a Destroyer (3), a Submarine (3) and a Patrol Boat (2). Drag a ship to move it and tap it to turn it. Ships can't touch each other, not even at the corners.",
     "<strong>Rozmísti flotilu.</strong> Každý kapitán má 5 lodí: letadlovou loď (5 políček), bitevní loď (4), torpédoborec (3), ponorku (3) a hlídkový člun (2). Loď přesuneš tažením a otočíš klepnutím. Lodě se nesmí dotýkat, ani rohem.",
     "<strong>Platziere deine Flotte.</strong> Jeder Kapitän hat 5 Schiffe: einen Flugzeugträger (5 Felder), ein Schlachtschiff (4), einen Zerstörer (3), ein U-Boot (3) und ein Patrouillenboot (2). Zieh ein Schiff, um es zu verschieben, und tippe darauf, um es zu drehen. Schiffe dürfen sich nicht berühren, auch nicht an den Ecken.",
     "<strong>Place ta flotte.</strong> Chaque capitaine a 5 navires : un porte-avions (5 cases), un cuirassé (4), un destroyer (3), un sous-marin (3) et un patrouilleur (2). Fais glisser un navire pour le déplacer et touche-le pour le tourner. Les navires ne peuvent pas se toucher, même par les coins.",
     "<strong>Posiziona la flotta.</strong> Ogni capitano ha 5 navi: una portaerei (5 caselle), una corazzata (4), un cacciatorpediniere (3), un sottomarino (3) e una motovedetta (2). Trascina una nave per spostarla e toccala per girarla. Le navi non possono toccarsi, nemmeno negli angoli."),
    ("<strong>Take turns firing.</strong> Tap a square in Enemy Waters to fire a cannonball. A splash means a miss and passes the turn. Flames mean a hit, and you fire again!",
     "<strong>Střílejte na střídačku.</strong> Klepni na políčko v nepřátelských vodách a vystřel dělovou kouli. Šplouchnutí znamená vedle a tah přechází na soupeře. Plameny znamenají zásah a střílíš znovu!",
     "<strong>Abwechselnd feuern.</strong> Tippe auf ein Feld in den feindlichen Gewässern, um eine Kanonenkugel abzufeuern. Ein Platscher heißt daneben, und der andere ist dran. Flammen heißen Treffer, und du schießt noch einmal!",
     "<strong>Tirez chacun à votre tour.</strong> Touche une case dans les eaux ennemies pour tirer un boulet de canon. Une éclaboussure veut dire raté, et c'est au tour de l'autre. Des flammes veulent dire touché, et tu tires encore !",
     "<strong>Sparate a turno.</strong> Tocca una casella nelle acque nemiche per sparare una palla di cannone. Uno spruzzo vuol dire mancato e il turno passa. Le fiamme vogliono dire colpito, e spari ancora!"),
    ("<strong>Sink them all.</strong> Hit every square of a ship to sink it. The first captain to sink the whole enemy fleet wins.",
     "<strong>Potop je všechny.</strong> Loď se potopí, když zasáhneš všechna její políčka. Vyhrává kapitán, který jako první potopí celou nepřátelskou flotilu.",
     "<strong>Versenke sie alle.</strong> Triff jedes Feld eines Schiffs, um es zu versenken. Wer zuerst die ganze feindliche Flotte versenkt, gewinnt.",
     "<strong>Coule-les tous.</strong> Touche toutes les cases d'un navire pour le couler. Le premier capitaine qui coule toute la flotte ennemie gagne.",
     "<strong>Affondale tutte.</strong> Colpisci tutte le caselle di una nave per affondarla. Vince il primo capitano che affonda tutta la flotta nemica."),
    ('<a href="privacy/">Privacy policy</a>', '<a href="privacy/">Ochrana soukromí</a>', '<a href="privacy/">Datenschutz</a>',
     '<a href="privacy/">Confidentialité</a>', '<a href="privacy/">Privacy</a>'),

    # ---- Privacy policy ----
    ("<title>Privacy policy · Cannonball Captains</title>", "<title>Ochrana soukromí · Cannonball Captains</title>",
     "<title>Datenschutzerklärung · Cannonball Captains</title>", "<title>Politique de confidentialité · Cannonball Captains</title>",
     "<title>Informativa sulla privacy · Cannonball Captains</title>"),
    ("Privacy policy for the Cannonball Captains game by Spidlen Games.", "Zásady ochrany soukromí hry Cannonball Captains od Spidlen Games.",
     "Datenschutzerklärung für das Spiel Cannonball Captains von Spidlen Games.", "Politique de confidentialité du jeu Cannonball Captains de Spidlen Games.",
     "Informativa sulla privacy del gioco Cannonball Captains di Spidlen Games."),
    ('<a href="./" aria-current="page">Privacy</a>', '<a href="./" aria-current="page">Soukromí</a>', '<a href="./" aria-current="page">Datenschutz</a>',
     '<a href="./" aria-current="page">Confidentialité</a>', '<a href="./" aria-current="page">Privacy</a>'),
    ('64px);">Privacy policy</h1>', '64px);">Ochrana soukromí</h1>', '64px);">Datenschutzerklärung</h1>', '64px);">Politique de confidentialité</h1>', '64px);">Informativa sulla privacy</h1>'),
    ('<p class="dim">Cannonball Captains, by Spidlen Games · Effective October 10, 2026</p>',
     '<p class="dim">Cannonball Captains od Spidlen Games · Platné od 10. října 2026</p>\n        <p class="dim">Toto je překlad. Platí <a href="/cannonball-captains/privacy/">anglická verze</a>.</p>',
     '<p class="dim">Cannonball Captains von Spidlen Games · Gültig ab 10. Oktober 2026</p>\n        <p class="dim">Dies ist eine Übersetzung. Maßgeblich ist die <a href="/cannonball-captains/privacy/">englische Fassung</a>.</p>',
     '<p class="dim">Cannonball Captains, par Spidlen Games · En vigueur depuis le 10 octobre 2026</p>\n        <p class="dim">Ceci est une traduction. Seule la <a href="/cannonball-captains/privacy/">version anglaise</a> fait foi.</p>',
     '<p class="dim">Cannonball Captains, di Spidlen Games · In vigore dal 10 ottobre 2026</p>\n        <p class="dim">Questa è una traduzione. Fa fede la <a href="/cannonball-captains/privacy/">versione inglese</a>.</p>'),
    ("The short version: Cannonball Captains has <strong>no ads, no analytics, no tracking and no accounts</strong>. Your captains stay on your device. Online games only share what the other player needs to see: your captain's name and character, and your moves.",
     "Ve zkratce: Cannonball Captains <strong>nemá reklamy, analytiku, sledování ani účty</strong>. Tvoji kapitáni zůstávají v tvém zařízení. Online hry sdílejí jen to, co musí vidět druhý hráč: jméno a postavičku tvého kapitána a tvoje tahy.",
     "Kurz gesagt: Cannonball Captains hat <strong>keine Werbung, keine Analyse, kein Tracking und keine Konten</strong>. Deine Kapitäne bleiben auf deinem Gerät. Online-Spiele teilen nur, was der andere Spieler sehen muss: Name und Figur deines Kapitäns und deine Züge.",
     "En bref : Cannonball Captains n'a <strong>ni pub, ni statistiques d'utilisation, ni pistage, ni comptes</strong>. Tes capitaines restent sur ton appareil. Les parties en ligne ne partagent que ce que l'autre joueur doit voir : le nom et le personnage de ton capitaine, et tes coups.",
     "In breve: Cannonball Captains <strong>non ha pubblicità, statistiche, tracciamento né account</strong>. I tuoi capitani restano sul tuo dispositivo. Le partite online condividono solo ciò che l'altro giocatore deve vedere: il nome e il personaggio del tuo capitano e le tue mosse."),
    ("<h2>What stays on your device</h2>", "<h2>Co zůstává v tvém zařízení</h2>", "<h2>Was auf deinem Gerät bleibt</h2>", "<h2>Ce qui reste sur ton appareil</h2>", "<h2>Cosa resta sul tuo dispositivo</h2>"),
    ("<li><strong>Captains:</strong> their names, chosen characters, any picture you upload as an avatar, and their wins and losses.</li>",
     "<li><strong>Kapitáni:</strong> jejich jména, vybrané postavičky, obrázky, které nahraješ jako avatar, a jejich výhry a prohry.</li>",
     "<li><strong>Kapitäne:</strong> ihre Namen, gewählten Figuren, Bilder, die du als Avatar hochlädst, und ihre Siege und Niederlagen.</li>",
     "<li><strong>Capitaines :</strong> leurs noms, les personnages choisis, les images que tu importes comme avatar, et leurs victoires et défaites.</li>",
     "<li><strong>Capitani:</strong> i loro nomi, i personaggi scelti, le immagini che carichi come avatar, e le loro vittorie e sconfitte.</li>"),
    ("<li><strong>Settings:</strong> sound and vibration on or off, and the language.</li>",
     "<li><strong>Nastavení:</strong> zvuk a vibrace zapnuto nebo vypnuto a jazyk.</li>",
     "<li><strong>Einstellungen:</strong> Ton und Vibration an oder aus, und die Sprache.</li>",
     "<li><strong>Réglages :</strong> son et vibrations activés ou non, et la langue.</li>",
     "<li><strong>Impostazioni:</strong> suono e vibrazione attivi o no, e la lingua.</li>"),
    ("<li><strong>An unfinished online game</strong>, so you can continue it, and a list of your recent online game codes, so old games can be cleaned up.</li>",
     "<li><strong>Nedohraná online hra</strong>, abys v ní mohl(a) pokračovat, a seznam kódů tvých posledních online her, aby se staré hry daly uklidit.</li>",
     "<li><strong>Ein unfertiges Online-Spiel</strong>, damit du es fortsetzen kannst, und eine Liste deiner letzten Online-Spielcodes, damit alte Spiele aufgeräumt werden können.</li>",
     "<li><strong>Une partie en ligne inachevée</strong>, pour pouvoir la reprendre, et la liste de tes codes de parties récentes, pour pouvoir nettoyer les anciennes parties.</li>",
     "<li><strong>Una partita online non finita</strong>, per poterla continuare, e un elenco dei codici delle tue partite online recenti, per poter eliminare le partite vecchie.</li>"),
    ("None of this is sent to us or anyone else, except as described under online games below. <strong>Avatars you upload never leave your device</strong>: other players see one of the built-in characters instead. Uninstalling the game deletes all of this.",
     "Nic z toho se neposílá nám ani nikomu jinému, kromě toho, co popisuje část o online hrách níže. <strong>Nahrané avatary nikdy neopustí tvé zařízení</strong>: ostatní hráči místo nich vidí jednu z vestavěných postaviček. Odinstalováním hry se tohle všechno smaže.",
     "Nichts davon wird an uns oder sonst jemanden gesendet, außer wie unten bei den Online-Spielen beschrieben. <strong>Hochgeladene Avatare verlassen nie dein Gerät</strong>: Andere Spieler sehen stattdessen eine der eingebauten Figuren. Wenn du das Spiel deinstallierst, wird all das gelöscht.",
     "Rien de tout cela ne nous est envoyé, ni à personne d'autre, sauf comme décrit plus bas pour les parties en ligne. <strong>Les avatars que tu importes ne quittent jamais ton appareil</strong> : les autres joueurs voient à la place un des personnages du jeu. Désinstaller le jeu efface tout cela.",
     "Niente di tutto questo viene inviato a noi o ad altri, tranne quanto descritto sotto per le partite online. <strong>Gli avatar che carichi non lasciano mai il tuo dispositivo</strong>: gli altri giocatori vedono invece uno dei personaggi del gioco. Disinstallare il gioco cancella tutto questo."),
    ("<h2>Online games</h2>", "<h2>Online hry</h2>", "<h2>Online-Spiele</h2>", "<h2>Parties en ligne</h2>", "<h2>Partite online</h2>"),
    ("Playing with a friend online uses <strong>Google Firebase</strong> (Realtime Database and anonymous Authentication), a service run by Google. When you play online:",
     "Hra s kamarádem online používá <strong>Google Firebase</strong> (Realtime Database a anonymní Authentication), službu provozovanou společností Google. Když hraješ online:",
     "Das Online-Spiel mit Freunden nutzt <strong>Google Firebase</strong> (Realtime Database und anonyme Authentication), einen Dienst von Google. Wenn du online spielst:",
     "Jouer avec un ami en ligne utilise <strong>Google Firebase</strong> (Realtime Database et Authentication anonyme), un service de Google. Quand tu joues en ligne :",
     "Giocare con un amico online usa <strong>Google Firebase</strong> (Realtime Database e Authentication anonima), un servizio gestito da Google. Quando giochi online:"),
    ("<li>The game signs in <strong>anonymously</strong>: Firebase gives your copy of the game a random ID. No name, email address or phone number is involved.</li>",
     "<li>Hra se přihlásí <strong>anonymně</strong>: Firebase přidělí tvé kopii hry náhodné ID. Žádné jméno, e-mailová adresa ani telefonní číslo se nepoužívá.</li>",
     "<li>Das Spiel meldet sich <strong>anonym</strong> an: Firebase gibt deiner Kopie des Spiels eine zufällige ID. Kein Name, keine E-Mail-Adresse und keine Telefonnummer.</li>",
     "<li>Le jeu se connecte <strong>anonymement</strong> : Firebase donne à ta copie du jeu un identifiant aléatoire. Aucun nom, adresse e-mail ou numéro de téléphone n'est utilisé.</li>",
     "<li>Il gioco accede <strong>in modo anonimo</strong>: Firebase assegna alla tua copia del gioco un ID casuale. Nessun nome, indirizzo email o numero di telefono.</li>"),
    ("<li>For each game, Firebase stores: the 4-letter game code; the two players' random IDs; each captain's <strong>name and built-in character</strong>; which version of the game they use; when each player was last connected; the <strong>shots</strong> fired and their results; and, at the end, each player's <strong>ship positions</strong> and a code that proves the fleet didn't change during the game.</li>",
     "<li>U každé hry Firebase ukládá: čtyřpísmenný kód hry; náhodná ID obou hráčů; <strong>jméno a vestavěnou postavičku</strong> každého kapitána; jakou verzi hry používají; kdy byl každý hráč naposledy připojen; vystřelené <strong>střely</strong> a jejich výsledky; a na konci <strong>pozice lodí</strong> každého hráče a kód, který dokazuje, že se flotila během hry nezměnila.</li>",
     "<li>Für jedes Spiel speichert Firebase: den Spielcode aus 4 Buchstaben; die zufälligen IDs der beiden Spieler; <strong>Name und eingebaute Figur</strong> jedes Kapitäns; welche Version des Spiels sie nutzen; wann jeder Spieler zuletzt verbunden war; die abgefeuerten <strong>Schüsse</strong> und ihre Ergebnisse; und am Ende die <strong>Schiffspositionen</strong> jedes Spielers und einen Code, der beweist, dass sich die Flotte während des Spiels nicht geändert hat.</li>",
     "<li>Pour chaque partie, Firebase enregistre : le code de partie de 4 lettres ; les identifiants aléatoires des deux joueurs ; le <strong>nom et le personnage</strong> de chaque capitaine ; la version du jeu utilisée ; quand chaque joueur était connecté pour la dernière fois ; les <strong>tirs</strong> et leurs résultats ; et, à la fin, la <strong>position des navires</strong> de chaque joueur et un code qui prouve que la flotte n'a pas changé pendant la partie.</li>",
     "<li>Per ogni partita, Firebase memorizza: il codice di 4 lettere; gli ID casuali dei due giocatori; il <strong>nome e il personaggio</strong> di ogni capitano; quale versione del gioco usano; quando ciascun giocatore è stato connesso l'ultima volta; i <strong>colpi</strong> sparati e i loro risultati; e, alla fine, le <strong>posizioni delle navi</strong> di ogni giocatore e un codice che dimostra che la flotta non è cambiata durante la partita.</li>"),
    ("<li>Only the two players in a game can read it. Your ship positions stay on your device until the game is over.</li>",
     "<li>Hru mohou číst jen její dva hráči. Pozice tvých lodí zůstávají v tvém zařízení, dokud hra neskončí.</li>",
     "<li>Nur die beiden Spieler eines Spiels können es lesen. Deine Schiffspositionen bleiben auf deinem Gerät, bis das Spiel vorbei ist.</li>",
     "<li>Seuls les deux joueurs d'une partie peuvent la lire. La position de tes navires reste sur ton appareil jusqu'à la fin de la partie.</li>",
     "<li>Solo i due giocatori di una partita possono leggerla. Le posizioni delle tue navi restano sul tuo dispositivo finché la partita non è finita.</li>"),
    ('<li>As with any internet service, Google receives your device\'s IP address when the game connects. See <a href="https://firebase.google.com/support/privacy">Firebase\'s privacy information</a>. The database is located in the United States.</li>',
     '<li>Jako u každé internetové služby dostane Google při připojení hry IP adresu tvého zařízení. Viz <a href="https://firebase.google.com/support/privacy">informace o soukromí Firebase</a>. Databáze je umístěna ve Spojených státech.</li>',
     '<li>Wie bei jedem Internetdienst erhält Google die IP-Adresse deines Geräts, wenn sich das Spiel verbindet. Siehe <a href="https://firebase.google.com/support/privacy">die Datenschutzinformationen von Firebase</a>. Die Datenbank befindet sich in den USA.</li>',
     '<li>Comme pour tout service Internet, Google reçoit l\'adresse IP de ton appareil quand le jeu se connecte. Voir <a href="https://firebase.google.com/support/privacy">les informations de confidentialité de Firebase</a>. La base de données se trouve aux États-Unis.</li>',
     '<li>Come per ogni servizio Internet, Google riceve l\'indirizzo IP del tuo dispositivo quando il gioco si connette. Vedi <a href="https://firebase.google.com/support/privacy">le informazioni sulla privacy di Firebase</a>. Il database si trova negli Stati Uniti.</li>'),
    ("<strong>How long it's kept:</strong> a game is deleted when it's over and its creator leaves, or when the last player leaves. Your device also deletes your games that are more than a day old the next time you open the game. A game that both players abandon may stay stored until one of them opens the game again, or until we remove it.",
     "<strong>Jak dlouho se uchovává:</strong> hra se smaže, když skončí a její zakladatel odejde, nebo když odejde poslední hráč. Tvé zařízení také smaže tvé hry starší než jeden den, až hru příště otevřeš. Hra, kterou oba hráči opustí, může zůstat uložená, dokud jeden z nich hru znovu neotevře, nebo dokud ji neodstraníme.",
     "<strong>Wie lange es gespeichert bleibt:</strong> Ein Spiel wird gelöscht, wenn es vorbei ist und sein Ersteller es verlässt, oder wenn der letzte Spieler es verlässt. Dein Gerät löscht außerdem deine Spiele, die älter als einen Tag sind, wenn du das Spiel das nächste Mal öffnest. Ein Spiel, das beide Spieler verlassen, kann gespeichert bleiben, bis einer von ihnen das Spiel wieder öffnet oder bis wir es entfernen.",
     "<strong>Durée de conservation :</strong> une partie est supprimée quand elle est terminée et que son créateur la quitte, ou quand le dernier joueur la quitte. Ton appareil supprime aussi tes parties de plus d'un jour la prochaine fois que tu ouvres le jeu. Une partie abandonnée par les deux joueurs peut rester enregistrée jusqu'à ce que l'un d'eux rouvre le jeu, ou jusqu'à ce que nous la supprimions.",
     "<strong>Per quanto tempo:</strong> una partita viene cancellata quando è finita e chi l'ha creata esce, o quando esce l'ultimo giocatore. Il tuo dispositivo cancella anche le tue partite più vecchie di un giorno la prossima volta che apri il gioco. Una partita abbandonata da entrambi i giocatori può restare memorizzata finché uno dei due non riapre il gioco, o finché non la rimuoviamo noi."),
    ("The captain name you choose is shown to the friend you play with, so it's a good idea to use a nickname or first name only.",
     "Jméno kapitána, které zvolíš, uvidí kamarád, se kterým hraješ, takže je dobré použít přezdívku nebo jen křestní jméno.",
     "Den Kapitänsnamen, den du wählst, sieht der Freund, mit dem du spielst. Nimm also am besten einen Spitznamen oder nur den Vornamen.",
     "Le nom de capitaine que tu choisis est montré à l'ami avec qui tu joues : mieux vaut utiliser un surnom ou seulement un prénom.",
     "Il nome del capitano che scegli viene mostrato all'amico con cui giochi, quindi è meglio usare un soprannome o solo il nome."),
    ("<h2>What we don't do</h2>", "<h2>Co neděláme</h2>", "<h2>Was wir nicht tun</h2>", "<h2>Ce que nous ne faisons pas</h2>", "<h2>Cosa non facciamo</h2>"),
    ("<li>No advertising, and no advertising IDs.</li>", "<li>Žádná reklama a žádná reklamní ID.</li>", "<li>Keine Werbung und keine Werbe-IDs.</li>",
     "<li>Pas de publicité, ni d'identifiants publicitaires.</li>", "<li>Niente pubblicità e niente ID pubblicitari.</li>"),
    ("<li>No analytics, crash reporting or tracking of any kind.</li>", "<li>Žádná analytika, hlášení pádů ani sledování jakéhokoli druhu.</li>",
     "<li>Keine Analyse, keine Absturzberichte und kein Tracking jeglicher Art.</li>", "<li>Pas de statistiques d'utilisation, de rapports de plantage ni de pistage d'aucune sorte.</li>",
     "<li>Niente statistiche, segnalazioni di arresti anomali o tracciamento di alcun tipo.</li>"),
    ("<li>No access to your contacts, location, camera, microphone or files. The game asks only for internet access (for online games) and vibration.</li>",
     "<li>Žádný přístup ke kontaktům, poloze, fotoaparátu, mikrofonu ani souborům. Hra žádá jen o přístup k internetu (kvůli online hrám) a o vibrace.</li>",
     "<li>Kein Zugriff auf Kontakte, Standort, Kamera, Mikrofon oder Dateien. Das Spiel fragt nur nach Internetzugang (für Online-Spiele) und Vibration.</li>",
     "<li>Aucun accès à tes contacts, ta position, ton appareil photo, ton micro ou tes fichiers. Le jeu demande seulement l'accès à Internet (pour les parties en ligne) et le vibreur.</li>",
     "<li>Nessun accesso a contatti, posizione, fotocamera, microfono o file. Il gioco chiede solo l'accesso a Internet (per le partite online) e la vibrazione.</li>"),
    ("<li>No selling or sharing of data with anyone.</li>", "<li>Žádný prodej ani sdílení dat s kýmkoli.</li>", "<li>Kein Verkauf und keine Weitergabe von Daten an irgendwen.</li>",
     "<li>Aucune vente ni aucun partage de données avec qui que ce soit.</li>", "<li>Nessuna vendita o condivisione di dati con nessuno.</li>"),
    ("<h2>Children</h2>", "<h2>Děti</h2>", "<h2>Kinder</h2>", "<h2>Enfants</h2>", "<h2>Bambini</h2>"),
    ("Cannonball Captains is made for families. It doesn't ask for anyone's age, real name, email address or any other contact details, and it has no chat. Players see each other only through a captain name and a built-in character.",
     "Cannonball Captains je hra pro rodiny. Neptá se na věk, skutečné jméno, e-mailovou adresu ani jiné kontaktní údaje a nemá chat. Hráči se navzájem vidí jen přes jméno kapitána a vestavěnou postavičku.",
     "Cannonball Captains ist für Familien gemacht. Es fragt nicht nach Alter, echtem Namen, E-Mail-Adresse oder anderen Kontaktdaten, und es hat keinen Chat. Spieler sehen voneinander nur einen Kapitänsnamen und eine eingebaute Figur.",
     "Cannonball Captains est fait pour les familles. Il ne demande ni l'âge, ni le vrai nom, ni l'adresse e-mail, ni aucune autre coordonnée, et il n'a pas de chat. Les joueurs ne se voient qu'à travers un nom de capitaine et un personnage du jeu.",
     "Cannonball Captains è fatto per le famiglie. Non chiede età, nome vero, indirizzo email o altri dati di contatto, e non ha chat. I giocatori si vedono solo attraverso il nome del capitano e un personaggio del gioco."),
    ("<h2>This website</h2>", "<h2>Tento web</h2>", "<h2>Diese Website</h2>", "<h2>Ce site</h2>", "<h2>Questo sito</h2>"),
    ('This website is hosted on GitHub Pages, which may record visitors\' IP addresses for security purposes. See <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub\'s privacy statement</a>. The site uses no cookies and no analytics.',
     'Tento web běží na GitHub Pages, které mohou z bezpečnostních důvodů zaznamenávat IP adresy návštěvníků. Viz <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">prohlášení GitHubu o ochraně soukromí</a>. Web nepoužívá cookies ani analytiku.',
     'Diese Website läuft auf GitHub Pages, das aus Sicherheitsgründen die IP-Adressen von Besuchern speichern kann. Siehe <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">die Datenschutzerklärung von GitHub</a>. Die Website nutzt keine Cookies und keine Analyse.',
     'Ce site est hébergé sur GitHub Pages, qui peut enregistrer l\'adresse IP des visiteurs pour des raisons de sécurité. Voir <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">la déclaration de confidentialité de GitHub</a>. Le site n\'utilise ni cookies ni statistiques.',
     'Questo sito è ospitato su GitHub Pages, che può registrare gli indirizzi IP dei visitatori per motivi di sicurezza. Vedi <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">l\'informativa sulla privacy di GitHub</a>. Il sito non usa cookie né statistiche.'),
    ("<h2>Changes and contact</h2>", "<h2>Změny a kontakt</h2>", "<h2>Änderungen und Kontakt</h2>", "<h2>Modifications et contact</h2>", "<h2>Modifiche e contatti</h2>"),
    ('If this policy changes, the new version will be posted on this page with a new date. Questions or requests (for example, to delete an online game): <span id="contact">contact details coming soon</span>.',
     'Pokud se tyto zásady změní, nová verze se objeví na této stránce s novým datem. Dotazy nebo žádosti (například o smazání online hry): <span id="contact">kontaktní údaje brzy doplníme</span>.',
     'Wenn sich diese Erklärung ändert, wird die neue Fassung mit neuem Datum auf dieser Seite veröffentlicht. Fragen oder Anliegen (zum Beispiel ein Online-Spiel löschen): <span id="contact">Kontaktdaten folgen in Kürze</span>.',
     'Si cette politique change, la nouvelle version sera publiée sur cette page avec une nouvelle date. Questions ou demandes (par exemple pour supprimer une partie en ligne) : <span id="contact">coordonnées bientôt disponibles</span>.',
     'Se questa informativa cambia, la nuova versione sarà pubblicata su questa pagina con una nuova data. Domande o richieste (per esempio, cancellare una partita online): <span id="contact">contatti in arrivo</span>.'),
]

NBSP = " "


def french(text):
    # French puts a no-break space before ! ? : ; and inside « », but not inside tags or links.
    parts = re.split(r"(<[^>]*>)", text)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r" ([!?:;»])", NBSP + r"\1", parts[i]).replace("« ", "«" + NBSP)
    return "".join(parts)


def pattern(english):
    pieces = [re.escape(piece) for piece in re.split(r"\s+", english.strip())]
    return re.compile(r"\s+".join(pieces))


def page_url(page, code):
    folder = page[: -len("index.html")]
    return "/" + ("" if code == "en" else code + "/") + folder


def picker(page, code):
    names = dict(LANGUAGES)
    links = "\n".join(
        f'          <li><a href="{page_url(page, other)}" hreflang="{other}" lang="{other}"'
        + (' aria-current="true"' if other == code else "") + f">{name}</a></li>"
        for other, name in LANGUAGES)
    return (f'<!-- languages: made by tools/languages.py -->\n'
            f'      <details class="lang">\n'
            f'        <summary aria-label="{names[code]}">{GLOBE} {code.upper()}</summary>\n'
            f'        <ul>\n{links}\n        </ul>\n      </details>\n'
            f'      <script>document.addEventListener("click", (e) => {{ const d = document.querySelector("details.lang"); '
            f'if (d && !d.contains(e.target)) d.open = false; }});</script>\n'
            f'      <!-- /languages -->')


def alternates(page):
    links = [f'  <link rel="alternate" hreflang="{code}" href="{SITE.rstrip("/")}{page_url(page, code)}">' for code, _ in LANGUAGES]
    links.append(f'  <link rel="alternate" hreflang="x-default" href="{SITE.rstrip("/")}{page_url(page, "en")}">')
    return "<!-- alternates: made by tools/languages.py -->\n" + "\n".join(links) + "\n  <!-- /alternates -->"


def add_generated(html, page, code):
    html = re.sub(r"<!-- languages: made by tools/languages.py -->.*?<!-- /languages -->", lambda _: picker(page, code), html, flags=re.S)
    if "<!-- alternates" not in html:
        html = html.replace("</head>", "  <!-- alternates: made by tools/languages.py -->\n  <!-- /alternates -->\n</head>", 1)
    return re.sub(r"<!-- alternates: made by tools/languages.py -->.*?<!-- /alternates -->", lambda _: alternates(page), html, flags=re.S)


def fix_links(html, page, code):
    """Links to shared files go one folder further up; screenshots and the game get this language."""
    folder = posixpath.dirname(page)

    def fix(match):
        attribute, value = match.group(1), match.group(2)
        if re.match(r"^([a-z]+:|#|/)", value):
            return match.group(0)
        target = posixpath.normpath(posixpath.join(folder, value))
        if not any((target + "/").startswith(shared) for shared in SHARED):
            return match.group(0)
        if target.startswith(SCREENS):
            target = SCREENS + code + "/" + target[len(SCREENS):]
        value = posixpath.relpath(target, posixpath.join(code, folder)) + ("/" if value.endswith("/") else "")
        if (target + "/").startswith("cannonball-captains/play/"):
            value += "?lang=" + code
        return f'{attribute}="{value}"'

    html = re.sub(r'\b(href|src)="([^"]+)"', fix, html)
    # The picture shown when a page is shared.
    return html.replace(SITE + SCREENS, SITE + SCREENS + code + "/")


def main():
    missing = []
    used = set()
    for page in PAGES:
        path = os.path.join(ROOT, page)
        with open(path) as f:
            english = add_generated(f.read(), page, "en")
        with open(path, "w") as f:
            f.write(english)
        for index, (code, _) in enumerate(LANGUAGES[1:], start=1):
            html = english.replace('<html lang="en">', f'<html lang="{code}">', 1)
            for row in sorted(TEXTS, key=lambda r: -len(r[0])):
                if row[index] is None:
                    continue
                translated = (french(row[index]) if code == "fr" else row[index]).strip()
                html, count = pattern(row[0]).subn(lambda _: translated, html)
                if count:
                    used.add(row[0])
            html = fix_links(add_generated(html, page, code), page, code)
            out = os.path.join(ROOT, code, page)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w") as f:
                f.write(html)
    for row in TEXTS:
        if row[1] is not None and row[0] not in used:
            missing.append(row[0])
    for text in missing:
        print("Not found in any page (did the English change?):", text[:90])
    print(f"Made {len(PAGES) * (len(LANGUAGES) - 1)} pages in {', '.join(c for c, _ in LANGUAGES[1:])}"
          + (f"; {len(missing)} texts not found" if missing else ""))


if __name__ == "__main__":
    main()
