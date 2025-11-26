-- Update the constraint on pages_count to allow values between 1 and 20
ALTER TABLE books DROP CONSTRAINT IF EXISTS books_pages_count_check;
ALTER TABLE books ADD CONSTRAINT books_pages_count_check CHECK (pages_count BETWEEN 1 AND 20);