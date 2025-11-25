'use client';

import { useEffect, useState } from 'react';
import { Vehicle } from '../../types';
import { api } from '../../utils/api';

export default function VehiclesPage() {
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        vehicle_id: '',
        type: '',
        tank_capacity_liters: '',
        reg_number: '',
        status: 'active' as 'active' | 'inactive'
    });

    useEffect(() => {
        fetchVehicles();
    }, []);

    const fetchVehicles = async () => {
        try {
            const data = await api.getVehicles({});
            setVehicles(data);
        } catch (error) {
            console.error('Error fetching vehicles:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.createVehicle({
                ...formData,
                tank_capacity_liters: parseFloat(formData.tank_capacity_liters)
            });
            setShowForm(false);
            setFormData({ vehicle_id: '', type: '', tank_capacity_liters: '', reg_number: '', status: 'active' });
            fetchVehicles();
        } catch (error) {
            console.error('Error creating vehicle:', error);
            alert('Error creating vehicle');
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this vehicle?')) return;
        try {
            await api.deleteVehicle(id);
            fetchVehicles();
        } catch (error) {
            console.error('Error deleting vehicle:', error);
            alert('Error deleting vehicle');
        }
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-xl)' }}>
                <h1 style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                    Fleet Management
                </h1>
                <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                    {showForm ? 'Cancel' : '+ Add Vehicle'}
                </button>
            </div>

            {showForm && (
                <form onSubmit={handleSubmit} className="card animate-slide-up" style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: 'var(--spacing-lg)' }}>Add New Vehicle</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--spacing-md)' }}>
                        <input
                            required
                            placeholder="Vehicle ID (e.g., V001)"
                            value={formData.vehicle_id}
                            onChange={(e) => setFormData({ ...formData, vehicle_id: e.target.value })}
                            style={{ padding: 'var(--spacing-sm)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}
                        />
                        <input
                            required
                            placeholder="Type (e.g., Excavator)"
                            value={formData.type}
                            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                            style={{ padding: 'var(--spacing-sm)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}
                        />
                        <input
                            required
                            type="number"
                            placeholder="Tank Capacity (liters)"
                            value={formData.tank_capacity_liters}
                            onChange={(e) => setFormData({ ...formData, tank_capacity_liters: e.target.value })}
                            style={{ padding: 'var(--spacing-sm)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}
                        />
                        <input
                            required
                            placeholder="Registration Number"
                            value={formData.reg_number}
                            onChange={(e) => setFormData({ ...formData, reg_number: e.target.value })}
                            style={{ padding: 'var(--spacing-sm)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}
                        />
                    </div>
                    <button type="submit" className="btn btn-primary" style={{ marginTop: 'var(--spacing-md)' }}>
                        Create Vehicle
                    </button>
                </form>
            )}

            {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-2xl)' }}>
                    <div className="spinner" />
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 'var(--spacing-lg)' }}>
                    {vehicles.map((vehicle) => (
                        <div key={vehicle.id} className="card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-md)' }}>
                                <h3 style={{ fontSize: '1.125rem', fontWeight: '600' }}>{vehicle.vehicle_id}</h3>
                                <span className={`badge ${vehicle.status === 'active' ? 'badge-low' : 'badge-medium'}`}>
                                    {vehicle.status}
                                </span>
                            </div>
                            <div style={{ fontSize: '0.875rem', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-md)' }}>
                                <div><strong>Type:</strong> {vehicle.type}</div>
                                <div><strong>Reg:</strong> {vehicle.reg_number}</div>
                                <div><strong>Capacity:</strong> {vehicle.tank_capacity_liters}L</div>
                                {vehicle.assigned_to_project && <div><strong>Project:</strong> {vehicle.assigned_to_project}</div>}
                            </div>
                            <button
                                className="btn btn-secondary"
                                style={{ width: '100%', fontSize: '0.75rem', padding: 'var(--spacing-xs) var(--spacing-sm)' }}
                                onClick={() => handleDelete(vehicle.vehicle_id)}
                            >
                                Delete
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {!loading && vehicles.length === 0 && (
                <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
                    <p style={{ color: 'var(--text-secondary)' }}>No vehicles in fleet. Add one to get started!</p>
                </div>
            )}
        </div>
    );
}
