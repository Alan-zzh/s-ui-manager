#!/usr/bin/env python3
"""
文件名: app.py
作者: Alan
版本: v1.0.0
功能: 傻瓜式Web规则管理器 - 像Shadowrocket一样管理规则
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

CONFIG_FILE = 'rules_config.json'
DATABASE_FILE = 'manager.db'

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            server TEXT NOT NULL,
            port INTEGER NOT NULL,
            uuid TEXT,
            password TEXT,
            group_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            group_name TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """首页"""
    init_database()
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM groups ORDER BY name')
    groups = cursor.fetchall()
    
    cursor.execute('SELECT * FROM rules ORDER BY priority DESC, id')
    rules = cursor.fetchall()
    
    cursor.execute('SELECT * FROM nodes ORDER BY name')
    nodes = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', groups=groups, rules=rules, nodes=nodes)

@app.route('/groups/add', methods=['POST'])
def add_group():
    """添加节点组"""
    name = request.form.get('name')
    description = request.form.get('description', '')
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO groups (name, description) VALUES (?, ?)', (name, description))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/groups/<int:group_id>/delete', methods=['POST'])
def delete_group(group_id):
    """删除节点组"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/nodes/add', methods=['POST'])
def add_node():
    """添加节点"""
    name = request.form.get('name')
    type_ = request.form.get('type')
    server = request.form.get('server')
    port = int(request.form.get('port'))
    uuid = request.form.get('uuid', '')
    password = request.form.get('password', '')
    group_id = request.form.get('group_id')
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO nodes (name, type, server, port, uuid, password, group_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, type_, server, port, uuid, password, group_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/nodes/<int:node_id>/delete', methods=['POST'])
def delete_node(node_id):
    """删除节点"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM nodes WHERE id = ?', (node_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/rules/add', methods=['POST'])
def add_rule():
    """添加规则"""
    type_ = request.form.get('type')
    value = request.form.get('value')
    group_name = request.form.get('group_name')
    priority = int(request.form.get('priority', 0))
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO rules (type, value, group_name, priority)
        VALUES (?, ?, ?, ?)
    ''', (type_, value, group_name, priority))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/rules/<int:rule_id>/delete', methods=['POST'])
def delete_rule(rule_id):
    """删除规则"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM rules WHERE id = ?', (rule_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/export', methods=['GET'])
def export_config():
    """导出配置为订阅生成器格式"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM groups')
    groups = cursor.fetchall()
    
    cursor.execute('SELECT * FROM rules ORDER BY priority DESC, id')
    rules = cursor.fetchall()
    
    cursor.execute('SELECT * FROM nodes')
    nodes = cursor.fetchall()
    
    conn.close()
    
    config = {
        'groups': [{'id': g[0], 'name': g[1], 'description': g[2]} for g in groups],
        'rules': [{'id': r[0], 'type': r[1], 'value': r[2], 'group_name': r[3], 'priority': r[4]} for r in rules],
        'nodes': [{'id': n[0], 'name': n[1], 'type': n[2], 'server': n[3], 'port': n[4], 'uuid': n[5], 'password': n[6], 'group_id': n[7]} for n in nodes]
    }
    
    return jsonify(config)

@app.route('/generate', methods=['POST'])
def generate_subscription():
    """生成订阅配置"""
    try:
        import subscription_generator
        
        generator = subscription_generator.SubscriptionGenerator()
        sub = generator.run('json')
        
        return jsonify({'success': True, 'subscription': sub})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("=" * 60)
    print("傻瓜式Web规则管理器")
    print("=" * 60)
    print("")
    print("访问地址: http://127.0.0.1:5000")
    print("")
    
    init_database()
    
    app.run(host='0.0.0.0', port=5000, debug=True)