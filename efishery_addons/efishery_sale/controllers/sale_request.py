import json
from odoo import http
from odoo.tools.config import config
from odoo.http import request, Response
import re

class PureControllerMixin(object):
    @staticmethod
    def patch_for_json(path_re):
        # this is to avoid Odoo, which assumes json always means json+rpc,
        # complaining about "function declared as capable of handling request
        # of type 'http' but called with a request of type 'json'"
        path_re = re.compile(path_re)
        orig_get_request = http.Root.get_request

        def get_request(self, httprequest):
            if path_re.match(httprequest.path):
                return http.HttpRequest(httprequest)
            return orig_get_request(self, httprequest)

        http.Root.get_request = get_request

class SaleOrderRequest(http.Controller, PureControllerMixin):

    # it means all response from endpoint with path /api/... will got purificiation from standard odoo POST/PUT HTTP response 
    PureControllerMixin.patch_for_json("^/api/")

    @http.route('/api/order', auth='public', csrf=False, methods=['PUT'])
    def update_order(self):
        data = json.loads((request.httprequest.data).decode())
        data_response = {}
        success_status = False
        headers_json = {'Content-Type': 'application/json'}
        access_token = str(request.env['ir.config_parameter'].sudo().get_param('efishery.static_token'))
        headers = http.request.httprequest.headers
        # check authorize by static token 
        if headers.get('Authorization') == access_token:
            request_update = data.get('data')
            if not request_update:
                response_status = "400 Bad Request"
                response_message = "Payload Request is empty"
            else:
                # search sale order by id 
                sale_order = request.env['sale.order'].sudo().browse(request_update.get('id'))
               
                if sale_order.state != "draft":
                    response_status = "400 Bad Request"
                    response_message = "sales order {}/{} state is {}, you can only update the sale order when state in draft/Quotation".format(sale_order.name, sale_order.external_reference, sale_order.state)
                else:
                    new_order_line = []
                    deleted_order_line = []
                    save_order_line = []
                    # check existing products in order line 
                    for update_line in request_update.get('order_line'):
                        existing_product = sale_order.order_line.filtered(lambda x:x.product_id.id == update_line['product_id'] and x.product_uom.id == update_line['product_uom'])
                        if existing_product:
                            if existing_product.price_unit != update_line['price_unit'] or existing_product.product_uom_qty != update_line['product_uom_qty']:
                                existing_product.price_unit = update_line['price_unit']
                                existing_product.product_uom_qty = update_line['product_uom_qty']
                        else:
                            new_order_line.append((0, 0, {
                                'product_id': update_line['product_id'],
                                'product_uom': update_line['product_uom'],
                                'product_uom_qty': update_line['product_uom_qty'],
                                'price_unit': update_line['price_unit']
                            }))

                    # update sale order 
                    sale_order.sudo().write({
                        'partner_id': request_update.get('partner_id'),
                        'date_order': request_update.get('date_order'),
                        'external_reference': request_update.get('external_reference'),
                        'order_line': new_order_line
                    })

                    # after we update the sale order, and the sale order is updated with new data,
                    # now we find the product and uom in sale order that isnt in order line request body
                    # to remove it from sale order
                    for update_line in request_update.get('order_line'):
                        existing_product = sale_order.order_line.filtered(lambda x:x.product_id.id == update_line['product_id'] and x.product_uom.id == update_line['product_uom'])
                        if existing_product:
                            save_order_line.append(existing_product.id)
                    
                    for remove_line in sale_order.order_line:
                        if remove_line.id not in save_order_line:
                            deleted_order_line.append((2, remove_line.id))

                    sale_order.order_line = deleted_order_line

                    success_status = True
                    response_status = "200 OK"
                    response_message = "sales order updated"
                    data_response = self.data_response_sale_order(sale_order)
        else:
            response_status = "401 Unauthorized"
            response_message = "Token Not Found"

        result = {
            "success": success_status,
            "message": response_message,
            "data": data_response
        }

        # return response 
        return Response(json.dumps(result), headers=headers_json, status=response_status)

    def data_response_sale_order(self, sale_order):
        result = {
            'so_id': sale_order.id,
            'partner_id': sale_order.partner_id.id,
            'date_order': str(sale_order.date_order),
            'external_reference': sale_order.external_reference,
            'so_number': sale_order.name,
            'order_line': [{
                'order_line_id': o_line.id,
                'product_id': o_line.product_id.id,
                'product_uom': o_line.product_uom.id,
                'product_uom_qty': o_line.product_uom_qty,
                'price_unit': o_line.price_unit
            } for o_line in sale_order.order_line]
        }

        return result

    @http.route('/api/order', auth='public', csrf=False, methods=['POST'])
    def create_order(self):
        data = json.loads((request.httprequest.data).decode())
        data_response = {}
        success_status = False
        headers_json = {'Content-Type': 'application/json'}
        access_token = str(request.env['ir.config_parameter'].sudo().get_param('efishery.static_token'))
        headers = http.request.httprequest.headers
        # check authorize by static token 
        if headers.get('Authorization') == access_token:
            request_order = data.get('data')
            if request_order: 
                if not request_order.get('partner_id') or not request_order.get('partner_id') \
                    or not request_order.get('date_order') or not request_order.get('company_id') \
                    or not request_order.get('order_line') or not request_order.get('external_reference'):
                    response_status = "400 Bad Request"
                    response_message = "Payload Request is not complete"
                else:
                    order_lines = [(0, 0, {
                        'product_id': line['product_id'],
                        'product_uom': line['product_uom'],
                        'product_uom_qty': line['product_uom_qty'],
                        'price_unit': line['price_unit']
                    }) for line in request_order.get('order_line')]
                    
                    # create new Sale Order.. we use admin as sales person, since we create it from external odoo UI
                    sale_order = request.env['sale.order'].sudo().create({
                        'partner_id': request_order.get('partner_id'),
                        'date_order': request_order.get('date_order'),
                        'external_reference': request_order.get('external_reference'),
                        'user_id': 2, 
                        'company_id': request_order.get('company_id'),
                        'order_line': order_lines
                    })

                    success_status = True
                    response_status = "200 OK"
                    response_message = "sales order created"
                    data_response = self.data_response_sale_order(sale_order)
            else:
                response_status = "400 Bad Request"
                response_message = "Payload Request is empty"
        else:
            response_status = "401 Unauthorized"
            response_message = "Token Not Found"

        result = {
            "success": success_status,
            "message": response_message,
            "data": data_response
        }

        # return response 
        return Response(json.dumps(result), headers=headers_json, status=response_status)
    
    def query_get_order_details(self, order_ids):
        # we use sql query to search data cause it's faster than odoo ORM..
        # on odoo 11-13 when we search data by using many table relation, 
        # odoo ORM is slower than we use sql query and inject it to the database
        # dunno about odoo14 but when i check the repo they still use some sql query on their code
        request.env.cr.execute("""
            SELECT 
                so.id as order_id
                , so.name
                , so.partner_id
                , so.date_order
                , so.company_id
                , json_build_object(
                    'partner', json_build_object(
                        'id', so.partner_id,
                        'name', rp.name,
                        'address', CONCAT(rp.street, ', ', rp.city)
                    ),
                    'company', json_build_object(
                        'id', so.company_id,
                        'name', rc.name,
                        'address', CONCAT(rcp.street, ', ', rcp.city)
                    )
                ) as relationship
                , jsonb_agg(
                    json_build_object(
                        'product', json_build_object(
                            'id', sol.product_id,
                            'name', pt.name,
                            'sku_code', pt.default_code,
                            'description', pt.description
                        ),
                        'uom', json_build_object(
                            'id', sol.product_uom,
                            'name', uom.name,
                            'description', uc.name
                        ),
                        'product_uom_qty', sol.product_uom_qty,
                        'price_unit', sol.price_unit
                    )
                ) as order_lines
            FROM sale_order so 
            JOIN res_partner rp ON so.partner_id = rp.id
            JOIN res_company rc ON so.company_id = rc.id
            JOIN res_partner rcp on rc.partner_id = rcp.id
            JOIN sale_order_line sol ON sol.order_id = so.id
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN uom_uom uom ON sol.product_uom = uom.id
            JOIN uom_category uc ON uom.category_id = uc.id
            WHERE 
                so.id IN ({})
            GROUP BY
                so.id, rp.id, rc.id, rcp.id
        """.format(
                (",".join(["'%s'" % (so_id) for so_id in order_ids]))
            )
        )

        return request.env.cr.dictfetchall()

    def get_order_details_state(self, order_ids):
        data = {}
        success_status = False
        response_message = ''
        if not order_ids:
            response_status = "400 Bad request"
            response_message = "order id not found"
        else:
            
            get_order_details = self.query_get_order_details(order_ids)

            # check if data that we search is found 
            if get_order_details:
                success_status = True
                response_status = "200 OK"
                response_message = "Data found"
                data = get_order_details
                
                for d in data:
                    # convert date time format to string, i got error serialize on date time field so i need to convert it to string first 
                    d['date_order'] = str(d['date_order'])
            else:
                response_status = "400 Bad request"
                response_message = "Sale Order by order id %s is not found" % (order_id)

        return {
            'response_status': response_status,
            'response_message': response_message,
            'success_status': success_status,
            'data': data
        }

    @http.route('/api/order', auth='public', methods=['GET'])
    def get_order_bulk(self):
        '''
            GET Sale Order Details by order id bulky
        '''
        data = json.loads((request.httprequest.data).decode())
        data_response = {}
        success_status = False
        headers_json = {'Content-Type': 'application/json'}
        access_token = str(request.env['ir.config_parameter'].sudo().get_param('efishery.static_token'))
        headers = http.request.httprequest.headers
        # check authorize by static token 
        if headers.get('Authorization') == access_token:
            # check if order_ids sent is zero/empty 
            order_ids = data.get('id')
            check_order_details = self.get_order_details_state(order_ids)
            response_status = check_order_details['response_status']
            response_message = check_order_details['response_message']
            success_status = check_order_details['success_status']
            data_response = check_order_details['data']
        else:
            response_status = "401 Unauthorized"
            response_message = "Token Not Found"

        result = {
            "success": success_status,
            "message": response_message,
            "data": data_response
        }

        # return response 
        return Response(json.dumps(result), headers=headers_json, status=response_status)

    @http.route('/api/order/<order_id>', auth='public', methods=['GET'])
    def get_order(self, order_id=0):
        '''
            GET Sale Order Details by order id
        '''
        data = {}
        success_status = False
        headers_json = {'Content-Type': 'application/json'}
        access_token = str(request.env['ir.config_parameter'].sudo().get_param('efishery.static_token'))
        headers = http.request.httprequest.headers
        # check authorize by static token 
        if headers.get('Authorization') == access_token:
            # check if order_id sent is zero/empty 
            order_ids = [order_id]
            check_order_details = self.get_order_details_state(order_ids)
            response_status = check_order_details['response_status']
            response_message = check_order_details['response_message']
            success_status = check_order_details['success_status']
            data = check_order_details['data'][0]
        else:
            response_status = "401 Unauthorized"
            response_message = "Token Not Found"

        result = {
            "success": success_status,
            "message": response_message,
            "data": data
        }

        # return response 
        return Response(json.dumps(result), headers=headers_json, status=response_status)
    