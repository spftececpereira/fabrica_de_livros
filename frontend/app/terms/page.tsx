import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <Link href="/">
          <Button variant="ghost" className="mb-8">
            Voltar para a página inicial
          </Button>
        </Link>
        
        <div className="prose prose-lg max-w-none">
          <h1 className="text-3xl font-bold mb-8 text-center">Termos de Serviço</h1>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">1. Aceitação dos Termos</h2>
            <p>
              Ao acessar e utilizar o serviço Fábrica de Livros, você concorda com estes Termos de Serviço e 
              todas as práticas e políticas aqui descritas. Se você não concorda com estes termos, não utilize 
              nosso serviço.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">2. Descrição do Serviço</h2>
            <p>
              Fábrica de Livros é uma plataforma que permite aos usuários criar livros de colorir personalizados 
              utilizando inteligência artificial. O serviço permite a geração de livros com base em descrições 
              fornecidas pelos usuários e estilos artísticos selecionados.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">3. Conta de Usuário</h2>
            <p>
              Ao criar uma conta, você é responsável por manter a confidencialidade de suas credenciais e por 
              todas as atividades que ocorram em sua conta. Você concorda em fornecer informações precisas e 
              completas ao criar sua conta.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">4. Limites de Uso</h2>
            <p>
              No plano gratuito, os usuários podem criar até 3 livros. Planos pagos oferecem geração ilimitada 
              de livros. A Fábrica de Livros se reserva o direito de modificar esses limites a qualquer momento, 
              com aviso prévio aos usuários.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">5. Propriedade Intelectual</h2>
            <p>
              As imagens geradas pela plataforma são de propriedade do usuário que as criou. A Fábrica de Livros 
              concede a você uma licença não exclusiva para usar, copiar e imprimir os livros gerados para fins 
              pessoais ou comerciais.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">6. Limitação de Responsabilidade</h2>
            <p>
              A Fábrica de Livros não se responsabiliza por danos diretos, indiretos, incidentais ou consequenciais 
              resultantes do uso do serviço. O uso do serviço é feito por sua conta e risco.
            </p>
          </section>
          
          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">7. Modificações nos Termos</h2>
            <p>
              Reservamo-nos o direito de modificar estes Termos de Serviço a qualquer momento. Alterações entrarão 
              em vigor após serem publicadas na plataforma. O uso contínuo do serviço constitui aceitação das 
              alterações.
            </p>
          </section>
          
          <section>
            <h2 className="text-2xl font-semibold mb-4">8. Contato</h2>
            <p>
              Para dúvidas sobre estes Termos de Serviço, entre em contato conosco através do e-mail: 
              suporte@fabricadelivros.com.br
            </p>
          </section>
        </div>
      </div>
    </div>
 );
}