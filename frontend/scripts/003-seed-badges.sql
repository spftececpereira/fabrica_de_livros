-- Insert initial badges
INSERT INTO badges (code, name, description, icon, category) VALUES
  ('first_book', 'Primeiro Livro', 'Criou seu primeiro livro de colorir', 'book', 'milestone'),
  ('five_books', 'Colecionador', 'Criou 5 livros de colorir', 'books', 'milestone'),
  ('ten_books', 'Mestre Criador', 'Criou 10 livros de colorir', 'trophy', 'milestone'),
  ('cartoon_style', 'Artista Cartoon', 'Criou um livro no estilo Cartoon', 'palette', 'style'),
  ('manga_style', 'Mangaká', 'Criou um livro no estilo Mangá', 'palette', 'style'),
  ('realistic_style', 'Realista', 'Criou um livro no estilo Realista', 'palette', 'style'),
  ('classic_style', 'Clássico', 'Criou um livro no estilo Clássico', 'palette', 'style'),
  ('story_teller', 'Contador de Histórias', 'Criou um livro com história educativa', 'book-open', 'creation'),
  ('max_pages', 'Épico', 'Criou um livro com 20 páginas', 'star', 'creation'),
  ('explorer', 'Explorador', 'Experimentou todos os 4 estilos artísticos', 'compass', 'special')
ON CONFLICT (code) DO NOTHING;
