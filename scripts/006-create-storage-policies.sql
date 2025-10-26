-- Storage policies
CREATE POLICY "Allow authenticated users to upload to books-images bucket"
  ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (bucket_id = 'books-images');

CREATE POLICY "Allow authenticated users to view files in books-images bucket"
  ON storage.objects FOR SELECT
  TO authenticated
  USING (bucket_id = 'books-images');