import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <Link href="/">
          <Button variant="ghost" className="mb-8">
            Voltar para a página inicial
          </Button>
        </Link>
        
        <div className="prose prose-lg max-w-none">
          <h1 className="text-3xl font-bold mb-8 text-center">Política de Privacidade</h1>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">1. Informações que Coletamos</h2>
            <p>
              Coletamos informações pessoais que você nos fornece diretamente ao criar uma conta, como nome, 
              endereço de e-mail e informações de autenticação do Google. Também coletamos informações sobre 
              os livros que você cria e como você utiliza nosso serviço.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">2. Como Utilizamos suas Informações</h2>
            <p>
              Utilizamos suas informações para:
            </p>
            <ul className="list-disc pl-6 mt-2">
              <li>Fornecer e melhorar nosso serviço de geração de livros</li>
              <li>Personalizar sua experiência na plataforma</li>
              <li>Comunicar-nos com você sobre atualizações e ofertas</li>
              <li>Garantir a segurança e integridade do nosso serviço</li>
            </ul>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">3. Informações Geradas</h2>
            <p>
              Os livros de colorir criados na plataforma são gerados por inteligência artificial, mas você 
              mantém todos os direitos sobre os livros que cria. As imagens geradas são armazenadas em nossos 
              servidores para que você possa acessá-las e baixá-las posteriormente.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">4. Compartilhamento de Informações</h2>
            <p>
              Não vendemos, comercializamos ou alugamos suas informações pessoais. Podemos compartilhar suas 
              informações apenas quando necessário para cumprir obrigações legais ou proteger nossos direitos.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">5. Segurança dos Dados</h2>
            <p>
              Implementamos medidas de segurança apropriadas para proteger contra acesso não autorizado, 
              alteração, divulgação ou destruição de suas informações pessoais. No entanto, nenhum método de 
              transmissão pela internet ou método de armazenamento eletrônico é 100% seguro.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">6. Cookies e Tecnologias Semelhantes</h2>
            <p>
              Utilizamos tecnologias como cookies para melhorar a funcionalidade do nosso serviço e entender 
              como você o utiliza. Você pode configurar seu navegador para recusar todos os cookies, mas isso 
              pode afetar a funcionalidade do nosso serviço.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">7. Seus Direitos</h2>
            <p>
              Você tem o direito de:
            </p>
            <ul className="list-disc pl-6 mt-2">
              <li>Acessar suas informações pessoais armazenadas conosco</li>
              <li>Corrigir informações imprecisas ou incompletas</li>
              <li>Excluir sua conta e informações associadas</li>
              <li>Revogar seu consentimento para o processamento de dados</li>
            </ul>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">8. Retenção de Dados</h2>
            <p>
              Mantemos suas informações pessoais pelo tempo necessário para fornecer nosso serviço, a menos 
              que uma retenção mais longa seja exigida ou permitida por lei. Quando sua conta é excluída, 
              removemos suas informações pessoais de forma segura.
            </p>
          </section>
          
          <section>
            <h2 className="text-2xl font-semibold mb-4">9. Contato</h2>
            <p>
              Para dúvidas sobre esta Política de Privacidade, entre em contato conosco através do e-mail: 
              privacidade@fabricadelivros.com.br
            </p>
          </section>
        </div>
      </div>
    </div>
 );
}