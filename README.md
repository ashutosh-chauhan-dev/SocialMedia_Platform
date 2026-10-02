# Pulse — SocialMedia_Platform

A portfolio-ready social media platform built with **Django 6.1** and server-rendered templates. This project was created for **CodeAlpha Full Stack Development Internship — Task 2**.

## Features

- User registration, login and secure POST logout
- Automatic user profiles with bio and avatar
- Create text posts with optional images
- Home feed containing your posts and posts from followed users
- Explore/search posts and usernames
- AJAX like/unlike without a page reload
- Comments on posts
- Follow/unfollow with followers and following lists
- Owner-only post deletion
- Django admin for content management
- Form validation and upload-size limits
- Environment-based production security settings
- Automated Django test suite covering core user and social flows

## Tech stack

- **Backend:** Django 6.1.1 / Python
- **Frontend:** Django Templates, HTML, CSS, vanilla JavaScript
- **Database:** SQLite for local development
- **Images:** Pillow
- **Testing:** Django TestCase

## Project structure

```text
social_project/          # Django project settings and root URLs
social/                   # Main application
  migrations/             # Database migrations
  templates/social/      # Server-rendered pages/components
  templatetags/           # Template helpers
  admin.py
  forms.py
  models.py
  signals.py
  tests.py
  urls.py
  views.py
static/
  css/style.css
  js/likes.js
media/
  avatars/.gitkeep
  posts/.gitkeep
.env.example
.gitignore
manage.py
requirements.txt
```

## Local setup — Windows PowerShell

```powershell
git clone https://github.com/ashutosh-chauhan-dev/SocialMedia_Platform.git
cd SocialMedia_Platform

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate
python manage.py check
python manage.py test

python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

If PowerShell blocks script activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the virtual environment again.

## Environment configuration

Copy `.env.example` to `.env` for reference. Django does not load `.env` automatically; for deployment, configure these variables through the hosting provider's environment-variable settings.

For local development, the project defaults to `DEBUG=True`.

For production, set at minimum:

```text
DJANGO_SECRET_KEY=<unique-random-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

The production configuration enables secure session/CSRF cookies, HTTPS redirect, HSTS, content-type sniffing protection, clickjacking protection, and a restrictive referrer policy.

## Testing

Run:

```powershell
python manage.py test
```

The test suite covers:

- Registration and password hashing
- Django password validation
- Login/logout behavior
- Authentication-required pages
- Feed visibility
- Post creation and deletion permissions
- Image-size validation
- Like/unlike behavior
- HTTP method restrictions
- Comment creation/validation
- Follow/unfollow behavior
- Self-follow protection
- Profile editing
- Avatar-size validation
- Public profile pages

For a deployment audit, also run:

```powershell
python manage.py check --deploy
```

Some deployment warnings are expected until the production environment supplies HTTPS, HSTS, and host configuration.

## Security notes

- Never commit `.env`, `db.sqlite3`, uploaded media, or virtual environments.
- Production secrets are read from environment variables.
- Logout and all state-changing actions use POST.
- Django CSRF protection is enabled.
- Post deletion is restricted to the post owner.
- Follow and like relationships are protected by database constraints.
- User-generated text is rendered through Django's normal template escaping.
- Uploaded post images and avatars have application-level size limits and Django/Pillow image validation.
- This project is suitable for a portfolio/internship submission. A real public deployment still requires infrastructure-specific review, HTTPS, database configuration, logging/monitoring, backups, and operational controls.

## License

This repository is intended as a student portfolio/internship project. Add a license if you plan to distribute or reuse it publicly.



