import BackendLoginForm from '../../src/components/BackendLoginForm';

export default function BackendLoginPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">BistroBoard</h1>
          <p className="text-gray-600">Restaurant-Supplier Management</p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <BackendLoginForm />
      </div>
    </div>
  );
}