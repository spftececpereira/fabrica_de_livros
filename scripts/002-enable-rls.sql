-- Enable Row Level Security
ALTER TABLE books ENABLE ROW LEVEL SECURITY;
ALTER TABLE pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;

-- Books policies
CREATE POLICY "Users can view own books"
  ON books FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own books"
  ON books FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own books"
  ON books FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own books"
  ON books FOR DELETE
  USING (auth.uid() = user_id);

-- Pages policies (users can only access pages from their books)
CREATE POLICY "Users can view pages from own books"
  ON pages FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM books
      WHERE books.id = pages.book_id
      AND books.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can create pages for own books"
  ON pages FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM books
      WHERE books.id = pages.book_id
      AND books.user_id = auth.uid()
    )
  );

-- User badges policies
CREATE POLICY "Users can view own badges"
  ON user_badges FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own badges"
  ON user_badges FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Badges are public (everyone can read)
ALTER TABLE badges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Badges are viewable by everyone"
  ON badges FOR SELECT
  USING (true);
