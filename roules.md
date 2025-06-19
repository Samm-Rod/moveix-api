## 📜 Regras de negócio do Moveix #001 — Aceitação Exclusiva de Fretes

## 🏷️ Nome:
Regra de Aceitação Exclusiva de Fretes

---

## 📄 Descrição:
Um pedido de frete só pode ser aceito por **um único motorista**.  
Após a aceitação, o pedido **deixa de ser exibido** para outros motoristas.

---

## 📌 Justificativa:
Evita disputas entre motoristas e garante prioridade ao primeiro que aceitar.  
Melhora a experiência do usuário e a organização da plataforma.

---

## ✅ Condições:
- O pedido de frete deve estar com status `disponível`
- O motorista deve estar com status `ativo` e **não estar em outra corrida**
- Ao ser aceito, o frete muda de status para `em andamento`

---

## ❌ Restrições:
- Não é possível aceitar fretes com status `em andamento`, `concluído` ou `cancelado`
- Motoristas suspensos ou com avaliação abaixo de 3 não podem aceitar novos fretes

---

## 🔁 Exceções:
- Se o motorista cancelar **antes do início da corrida**, o frete volta ao status `disponível`
- O pedido expira automaticamente após **24 horas sem ser aceito**

---

## 🧪 Exemplo de fluxo:

1. João (cliente) cria um novo pedido de frete
2. Maria (motorista) vê o frete na lista e clica em **"Aceitar"**
3. O sistema verifica:
   - O frete está disponível ✅  
   - Maria está ativa e sem corrida em andamento ✅
4. Frete muda para `em andamento`, atribuído a Maria
5. O pedido **não aparece mais para outros motoristas**

---
