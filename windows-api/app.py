from fastapi import FastAPI
from firebird.driver import connect

app = FastAPI()

DB_PATH = "localhost:C:\\FLEXXUS\\DB\\DB-REED COMPUTERS ARGENTINA SRL.fdb"
DB_USER = "READ_ONLY_APP"
DB_PASS = "Acc3so_Read!2026"


def query_to_json(cur, sql):
    cur.execute(sql)
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


@app.get("/articulos")
def get_articulos():
    with connect(DB_PATH, user=DB_USER, password=DB_PASS) as con:
        cur = con.cursor()
        return query_to_json(cur, "SELECT * FROM ARTICULOS")


@app.get("/stock")
def get_stock():
    sql = """
        SELECT A.Activo as ACTIVO, A.codigoparticular as REFERENCE,
            C.codigoarticulo as ID_SYNPROD,
            C.lote as LOTE,
            sum(C.stockactual) as STOCK,
            (case when sum(C.stockactual) <= 0 then 0 else 1 end) as STATUS,
            (SELECT A.muestraweb FROM articulos A where c.codigoarticulo = a.codigoarticulo) as MUESTRAWEB,
            sum(C.stockactual) - coalesce((Select Sum(CP.cantidad) AS Cantidad from CuerpoPedidos CP, CabezaPedidos A, Operaciones Op
                WHERE CP.CodigoArticulo = C.codigoarticulo and Cp.lote = C.lote and A.Anulada = 0
                and A.Operacion = Op.CodigoOperacion and Op.ComprometeStock = 1
                and CP.Cantidad - CP.CantidadRemitida > 0
                and CP.NumeroComprobante = A.NumeroComprobante
                And position(CP.CodigoDeposito in '001') > 0), 0) as STOCKR
        FROM stock S
        INNER JOIN Casilleros C ON S.codigoarticulo = C.codigoarticulo and S.Lote = C.Lote
        INNER JOIN ARTICULOS A ON A.codigoarticulo = C.codigoarticulo
        WHERE ('01/01/1900' <= '01/01/1900') or (('01/01/1900' > '01/01/1900') and (
            Exists (Select SC.codigoarticulo From Stock SC
                INNER JOIN Articulos A On A.CodigoArticulo = SC.CodigoArticulo
                where SC.codigoarticulo = S.codigoarticulo
                and ((SC.fechamodificacion >= '01/01/1900') or (A.fechamodificacion >= '01/01/1900')))
        ))
        group by A.Activo, A.codigoparticular, C.codigoarticulo, C.lote
    """
    with connect(DB_PATH, user=DB_USER, password=DB_PASS) as con:
        cur = con.cursor()
        return query_to_json(cur, sql)


@app.get("/price")
def get_price():
    sql = """
        SELECT A.codigoarticulo as ID_SYNPROD, 'R'||A.codigorubro as ID_CAT,
            A.codigoparticular as REFERENCE,
            A.codigomarca as ID_MAN, 0 as QUANTITY,
            A.preciopromocion1 as PRECIOPROMOCION,
            (case when A.activo = 1 and A.muestraweb = 1 and M.muestraweb = 1
                and R.muestraweb = 1 and SR.muestraweb = 1
                and GSR.muestraweb = 1 then 1 else 0 end) as STATUS,
            (case when A.preciosegunrubro = 0 then A.preciolista1 * MO.cambio
                else A.precioventa1 * MO.cambio end) as PRICE,
            A.descripcion as NAME,
            A.descripcioncortaweb as DESCRIPTION,
            (case when A.coeficientesegunrubro = 0 then A.coeficiente
                else R.coeficiente end) as TAX,
            A.destacadoweb as OUTSTANDING,
            A.fechamodificacion as LAST_DATE,
            A.pesoarticulo as WEIGHT
        FROM Articulos A
        INNER JOIN Monedas MO ON A.codigoMoneda = MO.codigoMoneda
        INNER JOIN Marcas M ON A.codigomarca = M.codigomarca
        INNER JOIN Rubros R ON A.codigorubro = R.codigorubro
        INNER JOIN superrubros SR ON R.codigosuperrubro = SR.codigosuperrubro
        INNER JOIN gruposuperrubros GSR ON SR.codigogruposuperrubro = GSR.codigogruposuperrubro
    """
    with connect(DB_PATH, user=DB_USER, password=DB_PASS) as con:
        cur = con.cursor()
        return query_to_json(cur, sql)
