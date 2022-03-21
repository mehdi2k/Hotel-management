# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo import models, fields, api


class HotelFloor(models.Model):
    _name = 'hotel.floor'
    _description = 'hotel floor'

    name = fields.Char(string="Floor", required=True, index=True)
    description = fields.Text()


class RoomType(models.Model):
    _name = 'room.type'
    _description = 'Room type'

    name = fields.Char(required=True, index=True)
    description = fields.Text()
    categ_id = fields.Many2one('room.type', 'Category')
    child_ids = fields.One2many('room.type', 'categ_id', 'Child Categories')


class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'hotel room'

    name = fields.Char(string='Room')
    floor_id = fields.Many2one('hotel.floor', help='At which floor the room is located.')
    max_adult = fields.Integer()
    max_child = fields.Integer()
    categ_id = fields.Many2one('room.type', string='Room Category', required=True)
    status = fields.Selection([('available', 'Available'), ('occupied', 'Occupied')], default='available')
    capacity = fields.Integer('Capacity', required=True)
    price = fields.Integer()

    @api.constrains('capacity')
    def check_capacity(self):
        for room in self:
            if room.capacity <= 0:
                raise ValidationError(_('Room capacity must be more than 0'))


class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _description = 'Reservation'

    name = fields.Char(string="Name", required='True')
    phone = fields.Char(string="Phone")
    email = fields.Char(string="E-Mail")
    address = fields.Char()
    identity = fields.Char(string="identity number", required='True')
    room_id = fields.Many2one('hotel.room', required='True')
    price = fields.Integer('Price per day', related='room_id.price')
    start_date = fields.Datetime(string="debut date")
    days = fields.Integer('number of days', required=True)
    image = fields.Binary()
    total = fields.Integer(compute='_total', string='total price')

    @api.onchange('price', 'days')
    def _total(self):
        if self.price and self.days:
            for record in self:
                record.total = record.price * record.days

    @api.constrains('start_date')
    def check_date(self):
        for dt in self:
            if dt.start_date < datetime.now():
                raise ValidationError(_('this date is old'))


class Client(models.Model):
    _name = 'hotel.client'

    name = fields.Many2one('hotel.reservation')
    folio_id = fields.Integer('folio number', required='True')
    days = fields.Integer('number of days', related='name.days')
    price = fields.Integer(related='name.total')
    client = fields.Char(string='client name', related='name.name')
