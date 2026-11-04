import { useState, type FormEvent } from 'react';
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router';
import { ApiError, errorMessage } from '../api/client';
import { useMe, useRegister } from '../api/queries';
import { Button, Field, Input, Notice, Select } from '../components/ui';
import { safeNext } from './LoginPage';

export function RegisterPage() {
  const [params] = useSearchParams();
  const next = safeNext(params.get('next'));
  const me = useMe();
  const register = useRegister();
  const navigate = useNavigate();
  const [form, setForm] = useState({ fullName: '', email: '', password: '', confirm: '' });
  const [createOrganization, setCreateOrganization] = useState(false);
  const [organization, setOrganization] = useState({
    name: '', slug: '', description: '', timezone: 'Asia/Kolkata',
  });
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});

  if (me.data) return <Navigate to={next} replace />;

  const serverErrors = register.error instanceof ApiError ? register.error.fieldErrors : {};
  const errors = { ...serverErrors, ...localErrors };
  const update = (field: keyof typeof form) => (value: string) => setForm((current) => ({ ...current, [field]: value }));

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const problems: Record<string, string> = {};
    if (form.fullName.trim().length < 2) problems.fullName = 'Enter your full name';
    if (!/^\S+@\S+\.\S+$/.test(form.email.trim())) problems.email = 'Enter a valid email address';
    if (form.password.length < 8) problems.password = 'Use at least 8 characters';
    if (form.password.length > 72) problems.password = 'Use at most 72 characters';
    if (form.confirm !== form.password) problems.confirm = 'The passwords do not match';
    if (createOrganization && organization.name.trim().length < 2) problems.organizationName = 'Enter an organization name';
    if (createOrganization && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(organization.slug.trim())) {
      problems.organizationSlug = 'Use lower-case letters, numbers and hyphens';
    }
    setLocalErrors(problems);
    if (Object.keys(problems).length > 0) return;
    register.mutate({
      fullName: form.fullName.trim(),
      email: form.email.trim(),
      password: form.password,
      ...(createOrganization ? {
        organizationName: organization.name.trim(),
        organizationSlug: organization.slug.trim(),
        organizationDescription: organization.description.trim(),
        organizationTimezone: organization.timezone,
      } : {}),
    },
      { onSuccess: () => navigate(next, { replace: true }) });
  };

  const generalError = register.isError && Object.keys(serverErrors).length === 0 ? errorMessage(register.error) : null;

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="text-2xl font-semibold text-stone-900">Create an account</h1>
      <p className="mt-1 text-sm text-stone-600">
        Already registered? <Link to="/login" className="text-pine-700 underline underline-offset-2">Log in</Link>
      </p>
      <form onSubmit={submit} className="mt-6 space-y-4 rounded-md border border-stone-200 bg-white p-5" noValidate>
        {generalError && <Notice tone="error">{generalError}</Notice>}
        <Field label="Full name" htmlFor="fullName" error={errors.fullName}>
          <Input id="fullName" autoComplete="name" value={form.fullName} invalid={!!errors.fullName}
                 onChange={(e) => update('fullName')(e.target.value)} />
        </Field>
        <Field label="Email" htmlFor="email" error={errors.email}>
          <Input id="email" type="email" autoComplete="email" value={form.email} invalid={!!errors.email}
                 onChange={(e) => update('email')(e.target.value)} />
        </Field>
        <Field label="Password" htmlFor="password" error={errors.password} hint="8 to 72 characters">
          <Input id="password" type="password" autoComplete="new-password" value={form.password} invalid={!!errors.password}
                 onChange={(e) => update('password')(e.target.value)} />
        </Field>
        <Field label="Confirm password" htmlFor="confirm" error={errors.confirm}>
          <Input id="confirm" type="password" autoComplete="new-password" value={form.confirm} invalid={!!errors.confirm}
                 onChange={(e) => update('confirm')(e.target.value)} />
        </Field>
        <label className="flex gap-2 text-sm text-stone-700">
          <input type="checkbox" checked={createOrganization} onChange={(e) => setCreateOrganization(e.target.checked)} />
          Create an organization and register me as its administrator
        </label>
        {createOrganization && (
          <div className="space-y-4 border-t border-stone-200 pt-4">
            <Field label="Organization name" htmlFor="organizationName" error={errors.organizationName}>
              <Input id="organizationName" value={organization.name}
                     onChange={(e) => setOrganization((current) => ({ ...current, name: e.target.value }))} />
            </Field>
            <Field label="Web address (slug)" htmlFor="organizationSlug" error={errors.organizationSlug}
                   hint="For example: sunrise-diagnostics">
              <Input id="organizationSlug" value={organization.slug}
                     onChange={(e) => setOrganization((current) => ({ ...current, slug: e.target.value.toLowerCase() }))} />
            </Field>
            <Field label="Description" htmlFor="organizationDescription">
              <Input id="organizationDescription" value={organization.description}
                     onChange={(e) => setOrganization((current) => ({ ...current, description: e.target.value }))} />
            </Field>
            <Field label="Time zone" htmlFor="organizationTimezone">
              <Select id="organizationTimezone" value={organization.timezone}
                      onChange={(e) => setOrganization((current) => ({ ...current, timezone: e.target.value }))}>
                {['Asia/Kolkata', 'Asia/Singapore', 'Asia/Dubai', 'Europe/London', 'Europe/Berlin',
                  'America/New_York', 'America/Los_Angeles', 'UTC'].map((zone) => (
                    <option key={zone} value={zone}>{zone}</option>
                  ))}
              </Select>
            </Field>
          </div>
        )}
        <Button type="submit" className="w-full" loading={register.isPending}>Create account</Button>
      </form>
      <p className="mt-4 text-xs text-stone-500">
        New accounts are visitor accounts. Staff access is given by the organization's administrator.
      </p>
    </div>
  );
}
