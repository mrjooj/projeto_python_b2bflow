-- Execute este script no SQL Editor do Supabase (Project > SQL Editor > New query)

create table if not exists contatos (
    id bigint generated always as identity primary key,
    nome text not null,
    telefone text not null,
    created_at timestamp with time zone default now()
);

-- Dados de exemplo (substitua pelos seus contatos reais antes de testar o envio)
insert into contatos (nome, telefone) values
    ('Maria', '5511999999999'),
    ('João', '5521988888888'),
    ('Ana', '5531977777777');
