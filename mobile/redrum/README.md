# REDRUM — Noahubai AI Hub mobil app

REDRUM egy Android alkalmazás (Capacitor + WebView alapú), amivel a Noahubai
AI Hub backendjét (FastAPI szerver: `main.py` / `backend/server.py`) lehet
távolról, mobilról felügyelni: rendszerállapot, ügynökök (Memory / Issue /
Fixer) állapota és újraindítása, valamint az automatikusan észlelt hibák
listája.

Az app **nem futtatja** magát a Python backendet a telefonon — egy általad
megadott szerver URL-t hív (saját szerver, VPS, otthoni hálózat stb.), amit
első indításkor, illetve a Beállítások képernyőn bármikor meg lehet
változtatni.

## Az APK beszerzése

### 1. Automatikus build GitHub Actionsben (ajánlott)

Minden, a `mobile/redrum/` mappát érintő push/PR, illetve manuális indítás
(`Actions` → `REDRUM Android APK` → `Run workflow`) legenerálja az APK-t a
GitHub futtatóján (ahol az Android SDK korlátlanul elérhető), és feltölti
build artifactként:

1. Nyisd meg a repo **Actions** fülét → **REDRUM Android APK** workflow.
2. Válaszd ki a legutóbbi (zöld pipa) futást.
3. Az **Artifacts** szekcióban töltsd le a `redrum-apk` csomagot — ebben van
   `REDRUM-debug.apk` (bármilyen Androidra azonnal telepíthető) és
   `REDRUM-release.apk` (a projekt saját aláíró kulcsával signelt, ez
   ajánlott végfelhasználói telepítéshez, mert a frissítések a helyükön
   felülírják egymást).

> Miért CI-ban épül? Ez a fejlesztői sandbox house policy miatt nem éri el a
> `dl.google.com`-ot (az Android SDK letöltési forrása), ezért itt helyben
> nem lehet ténylegesen lefordítani az APK-t. A GitHub Actions futtatón ez a
> korlátozás nem áll fenn, ezért oda van kiszervezve a tényleges build.

### 2. Helyi build (Android Studio / parancssor)

```bash
cd mobile/redrum
npm install
npx cap sync android
cd android
./gradlew assembleDebug      # gyors, azonnal telepíthető APK
./gradlew assembleRelease    # signelt, "éles" APK (redrum-release.keystore-dal)
```

Az elkészült fájlok itt lesznek:

- `android/app/build/outputs/apk/debug/app-debug.apk`
- `android/app/build/outputs/apk/release/app-release.apk`

Vagy nyisd meg az `android/` mappát Android Studio-val, és `Build ▸ Build
Bundle(s) / APK(s) ▸ Build APK(s)`.

## Telepítés a telefonra

1. Másold át az `.apk` fájlt a telefonra (link, felhő, USB, e-mail — bármi).
2. Nyisd meg a fájlkezelőben, engedélyezd az "Ismeretlen forrásból történő
   telepítést" a felugró kérésre (csak első alkalommal kell).
3. Telepítés → megnyitás.
4. Első indításkor add meg a Noahubai szerver URL-jét (pl.
   `https://szerver.example.com:8000` vagy `http://192.168.x.x:8000` helyi
   hálózaton) → **Csatlakozás**.

A `REDRUM-release.apk` mindig ugyanazzal a kulccsal van aláírva
(`android/keystore/redrum-release.keystore`), így egy újabb verzió
telepítése **frissítésként** megy végbe, nem kell előtte eltávolítani az
appot.

## Funkciók

- **Áttekintés** — élő rendszerstatisztika (aktív ügynökök, nyílt hibák,
  tanult minták), 8 másodpercenkénti automatikus frissítéssel.
- **Ügynökök** — a regisztrált ügynökök listája, egyenkénti újraindítási
  lehetőséggel (`POST /api/agents/{name}/restart`).
- **Hibák** — az Issue Agent által észlelt problémák súlyosság szerint.
- **Beállítások** — szerver URL módosítása/törlése, app-verzió infó.

Az app plain HTTP (nem TLS-es) szerverekkel is működik — ez szándékos, mert
sok Noahubai telepítés helyi hálózaton, tanúsítvány nélkül fut (lásd
`android/app/src/main/res/xml/network_security_config.xml`).

## Branding / assetek újragenerálása

Az ikonok és a splash screen szkripttel generáltak (`scripts/generate_assets.py`,
Pillow szükséges: `pip install Pillow`). Ha változik a márka (szín, logó,
név), a szkript módosítása után:

```bash
python3 scripts/generate_assets.py
npx cap sync android
```

## Fejlesztői kulcs — fontos megjegyzés

Az `android/keystore/redrum-release.keystore` egy **saját aláírású, csak
közvetlen (sideload) terjesztésre szánt** kulcs — nem publikus store-hoz
készült. Ha az appot valaha a Google Play-re szánjátok, generáljatok egy új,
biztonságosan tárolt (nem repóban lévő) kulcsot, és állítsátok be Play App
Signing-ot.
