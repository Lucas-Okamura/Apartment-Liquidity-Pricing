# Apartment-Liquidity-Pricing

# 1. Contexto

Em uma proptech, existe uma squad responsável por definir quais apartamentos a proptech deve listar na sua plataforma ou apostar na compra, de forma a permitir o crescimento de vendas em ritmo exponencial, a boa utilização dos recursos financeiros e unit economics saudáveis. As políticas criadas por esse squad influenciam diretamente a liquidez e risco do portfolio da empresa, tanto do ponto de vista financeiro (perdas para a proptech) quanto risco de comprometer a experiência do usuário (preços mal calibrados). As metas de portfolio definidas neste squad se desdobram na empresa, então é crítico que os modelos que suportam essas definições sejam assertivos, e que a estratégia de portfolio adotada siga uma lógica que faça sentido.

O desafio é criar um algoritmo de alocação de portfolio para decidir, entre os apartamentos disponíveis na target_apartments.csv, quais a proptech deve comprar, reformar e vender, no seguinte cenário:

* Pagam exatamente o valor pedido pelo proprietário (coluna value na base target_apartments.csv).
* A reforma traz o apartamento para o melhor estado de conservação possível (interior_quality=3).
* O capital disponível para compra dos apartamentos é de R$ 150 milhões.

Quais apartamentos você compraria (dentre os disponíveis na target_apartments.csv), e por qual preço você listaria esses apartamentos depois da reforma, de modo a maximizar a nossa receita esperada (valor de venda - valor de compra) por unidade de tempo (R$/dia)?

# 2. Problema de Negócio

* **Como é o contexto do problema?**

    * A proptech deseja investir na compra de mais apartamentos, reformá-los e vendê-los, para continuar o crescimento exponencial da empresa.
    
* **Qual é o objetivo?**
    
    * A proptech deseja descobrir quais são os melhores apartamentos para comprar e revender, sendo a liquidez e o preço de vendas algumas das principais variáveis a serem avaliadas. O capital disponível para a compra dos apartamentos é de R$ 150 milhões.
    
* **Por que é necessário?**

    * O time deseja maximizar o lucro por unidade de tempo com a revenda de apartamentos. Assim, é necessário definir preços de revenda e avaliar como esses preços impactam na liquidez do imóvel.
    
* **Como será a solução?**
    
    * Análise prescritiva, modificando variáveis, como preço e tempo até venda, para maximizar o lucro por unidade de tempo.
    * Uma tabela final com sugestões de apartamentos a serem comprados e reformados será fornecida via API, assim como o preço que tais apartamentos deverão ser vendidos.
    
# 3. Metodologia CRISP-DM

![](img/ciclo_crisp.png)

A ideia deste projeto é ser melhorado continuamente, ciclo após ciclo, aplicando as etapas de um projeto de Data Science especificadas acima, derivada do CRISP-DM, para Data Mining, utilizado aqui para projetos de Data Science.