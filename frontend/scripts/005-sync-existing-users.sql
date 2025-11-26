-- Sync any existing auth.users to public.users
INSERT INTO public.users (id, email, name, avatar_url, provider, provider_id)
SELECT 
  au.id,
  au.email,
  COALESCE(au.raw_user_meta_data->>'full_name', au.raw_user_meta_data->>'name', split_part(au.email, '@', 1)),
  au.raw_user_meta_data->>'avatar_url',
  COALESCE(au.raw_app_meta_data->>'provider', 'google'),
  au.raw_user_meta_data->>'sub'
FROM auth.users au
WHERE NOT EXISTS (
  SELECT 1 FROM public.users pu WHERE pu.id = au.id
);
