# Telegram Quiz Bot (Auto-publishing) — Render (Background Worker)

Ce bot publie automatiquement des **quiz** dans un **canal Telegram**, révèle la **réponse** après un délai, et inclut une **mini-leçon**. Thèmes inclus : 🇬🇧 Anglais et 🔐 Cybersécurité.

## 1) Créer le bot sur Telegram
1. Ouvre Telegram → cherche **BotFather**.
2. Tape `/newbot` → choisis un nom et un **username** unique (ex: `QuizEduCM_bot`).
3. Copie le **token** (on le collera sur Render comme `BOT_TOKEN`).

## 2) Préparer ton canal Telegram
1. Crée un **canal** (Public de préférence pour utiliser `@username`).  
2. Ajoute ton bot comme **Administrateur** avec droit de publier.
3. Note le **@username** du canal (ex: `@moncanaledu`) ou l’ID numérique (`-100…`).

## 3) Déployer sur Render (type: Background Worker)
1. Va sur https://dashboard.render.com → **New** → **Background Worker**.
2. Connecte ton GitHub et sélectionne ce dépôt (ou upload ces fichiers).
3. **Build Command** : `pip install -r requirements.txt`
4. **Start Command** : `python bot.py`
5. **Environment Variables** (Settings → Environment):
   - `BOT_TOKEN` = le token donné par BotFather
   - `CHANNEL_ID` = `@toncanal` (ou ID numérique ex: `-1001234567890`)
   - (optionnel) `TIMEZONE` = `Africa/Douala` (par défaut)
   - (optionnel) `DELAY_SECONDS` = `300` (5 minutes)
   - (optionnel) `TEST_MODE` = `1` pour tester (désactive l’horaire quotidien)
   - (optionnel) `TEST_INTERVAL_MINUTES` = `2` (toutes les 2 minutes)
   - (optionnel) `ENGLISH_HOUR`=`9`, `ENGLISH_MINUTE`=`0`
   - (optionnel) `CYBER_HOUR`=`18`, `CYBER_MINUTE`=`0`

## 4) Test rapide
- Mets `TEST_MODE=1` (et garde `TEST_INTERVAL_MINUTES=2`).  
- Déploie → au bout de quelques secondes le bot enverra un quiz toutes les 2 minutes en alternant les thèmes.
- Quand tout est OK, enlève `TEST_MODE` (ou mets `0`) pour revenir aux horaires quotidiens.

## 5) Astuces
- `CHANNEL_ID` peut être `@username` du canal — plus simple pour débuter.
- Assure-toi que le bot est **admin du canal**.
- Tu peux éditer les horaires via les variables `ENGLISH_*` et `CYBER_*`.
- Pour ajouter des questions, modifie la liste `QUIZ_DATA` dans `bot.py` (copie-colle une entrée et adapte).

Bon apprentissage et bonne cybersécurité !
