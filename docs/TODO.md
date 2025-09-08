##### ---------------------------------------------------------------------------
### Notes for Production Hardening
##### ---------------------------------------------------------------------------
* Add row-level permission checks as needed (e.g., community/space visibility, admin/moderator roles).
* Consider a simple profanity/abuse filter + moderation flags on posts/comments (e.g., is_hidden, moderation_status).
* Create background jobs to materialize denormalized counters if you need super fast counts at scale.
* Add rate limiting (per IP/user) to create_comment/create_post/react endpoints.
* Consider storing media in a separate table and referencing attachments from posts/comments.
* Add full-text search (PostgreSQL tsvector) on posts.content and comments.content.
* Use Alembic to generate migrations from these models; partial unique indexes require PostgreSQL.
* If you want deep nested trees in one shot, add an endpoint that uses a recursive CTE to fetch an entire subtree.

