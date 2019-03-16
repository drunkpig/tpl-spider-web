local cjson    = require 'cjson'
local pg = require('pgmoon')

local file_id = ngx.var.file_id   -- 用户的url里传过来的一串uuid
-- local strfmt   = string.format


local db = pg.new({host="127.0.0.1",port='5432', database="tpl_spider", user="postgres"})

local ok, err = db:connect()
if not ok then
    ngx.log(ngx.ERR, "failed to connect: ", err)
    return nil
end

sql = 'SELECT result FROM spider_task WHERE file_id='..db:escape_literal(file_id)
ngx.log(ngx.ERR, "exec sql: ", sql)
local rows, num_queries = db:query(sql)

if num_queries > 0 then
    -- print(cjson.encode(rows))
    -- out:
    -- [{"tablename":"products","tableowner":"xx"},{"tablename":"pg_statistic","tableowner":"postgres"}}]
    -- ngx.log(ngx.ERR, "failed to connect: "， cjson.encode(rows))
    ngx.log(ngx.ERR, "raw result: ", cjson.encode(rows))
    ngx.var.file_relative_path = rows[1]['result']
    ngx.log(ngx.ERR, "file_relative_path=", ngx.var.file_relative_path)
else
    ngx.var.file_relative_path = false
    ngx.log(ngx.ERR, "query error: ", err)
    ngx.var.file_relative_path = ""
    return nil
end

db:keepalive()
