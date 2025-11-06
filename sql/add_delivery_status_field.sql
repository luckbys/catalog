-- Adiciona campo delivery_status à tabela orders
-- Este campo é específico para rastrear o status da entrega

ALTER TABLE public.orders 
ADD COLUMN IF NOT EXISTS delivery_status character varying(20) NULL DEFAULT 'pending'::character varying;

-- Adiciona constraint para validar os valores permitidos
ALTER TABLE public.orders 
ADD CONSTRAINT orders_delivery_status_check 
CHECK (
  (delivery_status)::text = ANY (
    ARRAY[
      'pending'::character varying,
      'preparing'::character varying,
      'ready_for_pickup'::character varying,
      'in_transit'::character varying,
      'out_for_delivery'::character varying,
      'delivered'::character varying,
      'failed'::character varying,
      'returned'::character varying
    ]::text[]
  )
);

-- Cria índice para melhorar performance de consultas por delivery_status
CREATE INDEX IF NOT EXISTS idx_orders_delivery_status 
ON public.orders USING btree (delivery_status) 
TABLESPACE pg_default;

-- Comentários para documentação
COMMENT ON COLUMN public.orders.delivery_status IS 'Status específico da entrega do pedido';

-- Atualiza pedidos existentes baseado no status atual
-- Pedidos 'shipped' ou 'delivered' recebem status de entrega correspondente
UPDATE public.orders 
SET delivery_status = CASE 
  WHEN status = 'delivered' THEN 'delivered'
  WHEN status = 'shipped' THEN 'in_transit'
  WHEN status = 'processing' THEN 'preparing'
  WHEN status = 'confirmed' THEN 'preparing'
  ELSE 'pending'
END
WHERE delivery_status IS NULL OR delivery_status = 'pending';
