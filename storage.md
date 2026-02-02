---
layout: page
title: Storage Usage Report
permalink: /storage/
---

<div class="storage-report">
  <p>Storage usage across department servers. Highlighted entries indicate:</p>
  <ul>
    <li><span style="background-color: #fff3cd;">Yellow</span> - Current students using > 50GB</li>
    <li><span style="background-color: #ffe5b4;">Orange</span> - Alumni using > 10GB</li>
  </ul>

  {% if site.data.storage.servers %}
    {% for server_entry in site.data.storage.servers %}
      {% assign server_name = server_entry[0] %}
      {% assign server = server_entry[1] %}
      
      <h2 id="{{ server_name }}">{{ server_name | capitalize }}</h2>
      
      {% if server.doc_url %}
        <p><a href="{{ server.doc_url }}" target="_blank">📄 Documentation</a></p>
      {% endif %}
      
      {% if server.entries and server.entries.size > 0 %}
        <table>
          <thead>
            <tr>
              <th>Folder</th>
              <th>Usage</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {% for entry in server.entries %}
              <tr {% if entry.color %}style="background-color: {% if entry.color == 'yellow' %}#fff3cd{% elsif entry.color == 'orange' %}#ffe5b4{% endif %};"{% endif %}>
                <td><code>{{ entry.folder }}</code></td>
                <td>{{ entry.usage }}</td>
                <td>
                  {% if entry.profile_url %}
                    <a href="{{ entry.profile_url }}" target="_blank">Profile</a>
                  {% endif %}
                </td>
              </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p><em>No data available</em></p>
      {% endif %}
    {% endfor %}
  {% else %}
    <p><em>No storage data available. Please run data generation.</em></p>
  {% endif %}
</div>

<style>
  .storage-report table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
  }
  .storage-report th,
  .storage-report td {
    padding: 8px 12px;
    text-align: left;
    border: 1px solid #ddd;
  }
  .storage-report th {
    background-color: #0b3d91;
    color: white;
    font-weight: bold;
  }
  .storage-report tr:nth-child(even) {
    background-color: #f9f9f9;
  }
  .storage-report code {
    font-family: monospace;
    font-size: 0.9em;
  }
</style>
